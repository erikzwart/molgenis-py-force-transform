'''Get dataframe from REDCap CDISC ODM and convert to datamodel aka molgenis.csv'''
import configparser
import re
from typing import Dict
import pandas as pd

import src.cdisc
import src.emx2
import src.export
import src.REDCap.utils
#from cdisc import Cdisc
#from emx2 import Emx2
#from export import export

#from REDCap.utils import defined_instruments, datamodel_table_columns


class REDCapDatamodel:
    config = configparser.ConfigParser()
    config.read('./src/config.ini')
    
    ns = config['redcap']['namespace']
    datamodel = config['settings']['datamodel']
    subject_data_name = config['settings']['subject'].split(".")[0]

    def __init__(self, file: str) -> None:
        self.file = file
    
    def subject_data(self) -> None:
        self.generate_subjectdata()
    
    def instruments(self) -> None:
        self.generate_instruments(to_csv = True, to_dataframe = False)

    def generate_subjectdata(self) -> None:
        #result = self.table_columns()
        result = src.REDCap.utils.datamodel_table_columns()
        result = result.append({'tableName': self.subject_data_name}, ignore_index=True)
        result = result.append({
            'tableName': self.subject_data_name,
            'columnName': 'key',
            'key': '1', 
            'required': 'TRUE'}, ignore_index=True)
        result = result.append({
            'tableName': self.subject_data_name,
            'columnName': 'SubjectKey',
            'required': 'TRUE'}, ignore_index=True)
        result = result.append({
            'tableName': self.subject_data_name,
            'columnName': 'FormRepeatKey',
            'required': 'TRUE'}, ignore_index=True)
        result = result.drop(columns=['DataType','FieldType','TextValidationType'])     
        src.export.export.instrument_to_csv(result, self.datamodel)
    
    def generate_instruments(self, to_csv: bool = False, to_dataframe: bool = False) -> None:
        '''generate intruments in datamodel aka molgenis.csv format'''
        def instrument_table(dataframe: pd.DataFrame, instrument: str) -> pd.DataFrame:
            '''instrument row returns pd.DataFrame'''
            result = dataframe.append({'tableName': instrument}, ignore_index=True)
            result = result.append({
                'tableName': instrument,
                'columnName': 'key',
                'columnType': 'ref',
                'refTable': self.subject_data_name,
                'key': '1', 
                'required': 'TRUE'}, ignore_index=True)
            result = result.append({
                'tableName': instrument,
                'columnName': 'SubjectKey',
                'required': 'TRUE'}, ignore_index=True)
            result = result.append({
                'tableName': instrument,
                'columnName': 'FormRepeatKey'}, ignore_index=True)
            return result
        
        

        def dataframe_defined_instruments() -> pd.DataFrame:
            result = src.REDCap.utils.datamodel_table_columns()
            for instrument in src.REDCap.utils.defined_instruments(self.file, self.ns):
                result = instrument_table(result, instrument)
            return result
            
        def dataframe_defined_variables(dataframe: pd.DataFrame) -> pd.DataFrame:
            ''''''
            result = dataframe
            xml = src.cdisc.Cdisc(self.file, 'REDCap')

            def defined_variables() -> list:
                '''return list of defined variables'''
                return src.cdisc.Cdisc.attribute_values(xml, './/odm:ItemGroupDef', 'OID')

            def variable_description(variable: str) -> str:
                '''return FieldNote for given variable'''
                return src.cdisc.Cdisc.attribute_value(xml, ".//odm:ItemDef[@OID='"+ variable +"']", self.ns + 'FieldNote')
            
            def variable_datatype(variable: str) -> str:
                '''return DataType for given variable'''
                return src.cdisc.Cdisc.attribute_value(xml, ".//odm:ItemDef[@OID='"+ variable +"']", 'DataType')

            def variable_fieldtype(variable: str) -> str:
                '''return FieldType for given variable'''
                return src.cdisc.Cdisc.attribute_value(xml, ".//odm:ItemDef[@OID='"+ variable +"']", self.ns + 'FieldType')

            def variable_textvalidationtype(variable: str) -> str:
                '''return TextValidationType for given variable'''
                return src.cdisc.Cdisc.attribute_value(xml, ".//odm:ItemDef[@OID='"+ variable +"']", self.ns + 'TextValidationType')
            
            def variable_table(dataframe: pd.DataFrame, data: Dict[str, str]) -> pd.DataFrame:
                '''variable row returns pd.DataFrame'''
                return dataframe.append({
                    'tableName': data['tableName'],
                    'columnName': data['columnName'],
                    'description': data['description'],
                    'DataType': data['DataType'],
                    'FieldType': data['FieldType'],
                    'TextValidationType': data['TextValidationType']
                }, ignore_index=True)
            
            def fetch_variable_field(dataframe: pd.DataFrame, variable_row: src.cdisc.Cdisc, tablename: str) -> pd.DataFrame:
                '''fetch variable fields and return DataFrame'''
                def collapse_multiple_choice(variable_str: str) -> str:
                    '''to collapse multiple choice to EMX format later'''
                    return re.sub('___\d+$', '', variable_str)
                
                result = dataframe
                tablename = tablename.split('.')[0]
                
                for c in variable_row['ItemOID']:
                    dict = {
                        'tableName': tablename,
                        'columnName': collapse_multiple_choice(c),
                        'description': variable_description(c),
                        'DataType': variable_datatype(c),
                        'FieldType': variable_fieldtype(c),
                        'TextValidationType': variable_textvalidationtype(c)
                    }
                    result = variable_table(result, dict)
                return result

            for variable in defined_variables():
                variable_row = src.cdisc.Cdisc.attributes(xml, ".//odm:ItemGroupDef[@OID='"+ variable +"']/")
                result = fetch_variable_field(result, variable_row, variable)
            return result

        # export to file or return dataframe
        if to_csv:
            result = dataframe_defined_instruments()
            result = dataframe_defined_variables(result)
            result = result.drop_duplicates(subset = ["columnName"]) # drop duplicates (from multiple choice questions)  
            result = src.emx2.Emx2.REDCap_datatype(result) # determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
            result = result.drop(columns=['DataType','FieldType','TextValidationType']) # remove REDCap columns
            src.export.export.instrument_to_csv(result, self.datamodel)

        if to_dataframe:
            result = dataframe_defined_instruments()
            result = dataframe_defined_variables(result)
            #result = result.drop_duplicates(subset = ["columnName"]) # drop duplicates (from multiple choice questions)  
            result = src.emx2.Emx2.REDCap_datatype(result) # determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
            #result = result.drop(columns=['DataType','FieldType','TextValidationType']) # remove REDCap columns
            return result
