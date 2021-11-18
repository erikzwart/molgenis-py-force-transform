import pandas as pd
import numpy as np
import sys

from src.molgenis.cdisc import Cdisc
from src.molgenis.emx2 import Emx2, Molgenis


class REDCap:
    '''

    '''          
    # set namespace for REDCap CDISC ODM
    ns = '{https://projectredcap.org}'
            
    def main(self, file: str, edc: str):
        self.doc = Cdisc(file, edc)
        # set namespace for REDCap CDISC ODM
        ns = REDCap.ns
        # set output path
        path = './data/output/'
         # see if REDCap xml contains clinical data, if not exit
        if not Cdisc.attribute_value(self.doc, ".//odm:ClinicalData", 'StudyOID'):
            sys.exit('No ClinicalData found for this Study, exiting.')

        # see if Study contains repeating instruments
        repeatingInstrument = Cdisc.attribute_values(self.doc, ".//" + ns + "RepeatingInstrument", ns + "RepeatInstrument")
        if not repeatingInstrument:
            repeatingInstrument = {False}
        else:
            repeatingInstrument = set(repeatingInstrument)
        
        # retrieve the instruments defined by REDCap
        instruments = Cdisc.attribute_values(self.doc, './/odm:FormDef', ns + 'FormName')

        ### molgenis.csv ###
        #
        # create empty molgenis.csv and add columns
        # - added the following extra columns to be able to determine columnType
        #   DataType
        #   FieldType
        #   TextValidationType
        df = Molgenis.table_columns()

        # append instrument (tables) to molgenis.csv
        #df = Molgenis.instrument_table(df, instrument)

        # retrieve variables for each instrument (table)
        variables = Cdisc.attribute_values(self.doc, './/odm:ItemGroupDef', 'OID')
        
        for instrument in instruments:
            # append instrument (tables) to molgenis.csv
            df = Molgenis.instrument_table(df, instrument)


        for v in variables:
            column = Cdisc.attributes(self.doc, ".//odm:ItemGroupDef[@OID='"+ v +"']/")
            
            instrument = v.split('.')
            instrument = instrument[0]


            for c in column['ItemOID']:
                description = Cdisc.attribute_value(
                    self.doc, 
                    ".//odm:ItemDef[@OID='"+ c +"']", 
                    ns + 'FieldNote'
                )
                data_type = Cdisc.attribute_value(
                    self.doc, 
                    ".//odm:ItemDef[@OID='"+ c +"']", 
                    'DataType'
                )
                field_type = Cdisc.attribute_value(
                    self.doc, 
                    ".//odm:ItemDef[@OID='"+ c +"']", 
                    ns + 'FieldType'
                )
                text_validation_type = Cdisc.attribute_value(
                    self.doc, 
                    ".//odm:ItemDef[@OID='"+ c +"']",
                    ns + 'TextValidationType'
                )
                
                data = [instrument, c, description, data_type, field_type, text_validation_type]
                df = Molgenis.variable_table(df, data)

        # Determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
        df = Emx2.datatype(df)
        # Transform and output a valid molgenis.csv from Pandas DataFrame
        Molgenis.write_molgenis_csv(df, path, 'molgenis.csv')

        ### Clinical data ###
        #
        # setup data MultiIndex DataFrame
        columns = pd.MultiIndex.from_frame(REDCap.__form_variables(self, df))
        index = pd.MultiIndex.from_product([[],[]], names=['SubjectKey','FormRepeatKey'])
        clinicalData = pd.DataFrame([], index=index, columns=columns)

        # determine if repeated measurments are used
        StudyEventData = Cdisc.attributes(self.doc, './/odm:StudyEventData')
        
        # retrieve SubjectKeys
        SubjectKeys = Cdisc.attribute_values(self.doc, './/odm:SubjectData', 'SubjectKey')

        try:
            if StudyEventData == None:
                # No repeated instruments found, get clinicalData
                clinicalData = REDCap.__clinical_data_no_repeats(self, SubjectKeys, clinicalData)
        except ValueError:
            # Repeated instruments, get clinicalData
            clinicalData = REDCap.__clinical_data_repeats(self, SubjectKeys, clinicalData)
        
        ### transform clinical data
        # 
        # retrieve instrument name and OID
        instruments = REDCap.__get_forms(self)

        # transform clinicalData for each instrument
        for i in instruments.index:
            instrument_name = instruments['FormName'][i]
            instrument_data = clinicalData[instruments['OID'][i]]
            
            transformed_clinicalData = REDCap.__transform_redcap_boolean(self, df, instrument_data)

            # see if instrument is a repeating instrument, returns bool
            repeating = [True if i == instrument_name else False for i in repeatingInstrument][0]
            
            Molgenis.write_instrument_csv(transformed_clinicalData, path, instrument_name, repeating)
        
        ### SubjectData
        FormRepeatKeys = Cdisc.attribute_values(self.doc, './/odm:FormData', 'FormRepeatKey')
        Molgenis.subjectData_table(SubjectKeys, FormRepeatKeys, path, 'SubjectData.csv')

    def __transform_redcap_boolean(
        self, 
        df: pd.DataFrame, 
        instrument_data: pd.DataFrame) -> pd.DataFrame:
        '''Transform REDCap bool (0/1) to EMX2 TRUE/FALSE'''
        field_types: list = ['truefalse', 'yesno']
        columns = list(instrument_data.columns)

        data_copy = instrument_data.copy()

        # see if REDCap variable is defined as boolean
        for c_name in columns:          
            # check if variable (c) is defined as boolean and one of the field_types
            for f_type in field_types:
                row = df.loc[
                    (df['DataType'] == 'boolean') & 
                    (df['FieldType'] == f_type) & 
                    (df['columnName'] == c_name)]
                
                if row.index.notnull():
                    data_copy[c_name] = data_copy[c_name].replace(['0'],'FALSE')
                    data_copy[c_name] = data_copy[c_name].replace(['1'],'TRUE')
        return data_copy

    def __clinical_data_repeats(self, SubjectKeys: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
        '''Retrieve clinicaldata from study with repeated measurements'''
        for SubjectKey in SubjectKeys:

            SubjectData = Cdisc.iterfind(self.doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

            for i in SubjectData:
                for j in i:
                    for k in j:
                        for l in k:
                            data.loc[(SubjectKey,j.attrib['FormRepeatKey']),
                                ([j.attrib['FormOID']],[l.attrib['ItemOID']])] = l.attrib['Value']
        return data

    def __clinical_data_no_repeats(
        self, 
        SubjectKeys: np.ndarray, 
        data: pd.DataFrame) -> pd.DataFrame:
        """Retrieve clinicaldata from study without repeated measurements"""
        for SubjectKey in SubjectKeys:

            SubjectData = Cdisc.iterfind(self.doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

            for i in SubjectData:
                    for j in i:
                        for k in j:
                            try:
                                data.loc[(SubjectKey,i.attrib['FormRepeatKey']),
                                    ([i.attrib['FormOID']],[k.attrib['ItemOID']])] = k.attrib['Value']
                            except KeyError:
                                # in case of images or files a value attribute does not exists
                                # TODO
                                # images/files
                                data.loc[(SubjectKey,i.attrib['FormRepeatKey']),
                                    ([i.attrib['FormOID']],[k.attrib['ItemOID']])] = ''
        return data

    def __form_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        '''Returns a pandas DataFrame with two columns: FormOID, ItemOID of all Forms used by the Study'''
        forms = REDCap.__get_forms(self)

        df = df[['tableName','columnName']]
        df = df.dropna(subset=['columnName'])

        v = pd.merge(forms, df, left_on='FormName', right_on='tableName')
        v = v.drop(['FormName'], axis=1)
        v = v.drop(['tableName'], axis=1)

        v.rename(columns={'OID': 'FormOID', 'columnName': 'ItemOID'}, inplace=True)

        return v
        
    def __get_forms(self) -> pd.DataFrame:
        '''Returns a pandas DataFrame with to columns: OID, FormName'''
        ns = REDCap.ns
        # determine which forms are included and need to be extracted
        forms = pd.concat([
            pd.Series(Cdisc.attribute_values(self.doc, './/odm:FormDef', 'OID'), name='OID'), 
            pd.Series(Cdisc.attribute_values(self.doc, './/odm:FormDef', ns + 'FormName'), name='FormName')], axis=1)
            #pd.Series(Cdisc.attribute_values(self.doc, './/odm:FormDef', 'redcap:FormName'), name='FormName')], axis=1)
        return forms