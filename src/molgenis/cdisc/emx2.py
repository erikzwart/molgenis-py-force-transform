import re
import pandas as pd
import numpy as np

from src.molgenis.cdisc.odm import Redcap

class Transform:
    """Transform CDISC ODM to EMX2"""

    def __init__(self, file: str) -> None:
        self.doc = Redcap(file)

        self.molgenis()
        self.clinical_data()

    def molgenis(self) -> None:
        """Make molgenis.csv"""
        # molgenis.csv column names
        # added columns DataType, FieldType and TextValidationType to later determine the columnType
        self.molgenis_table_columns()
        # get the table name(s)
        self.molgenis_table()
        # Transform REDCap datatype to EMX2
        self.emx2_datatype()
        # Build and write molgenis.csv
        self.molgenis_csv()

    def molgenis_table_columns(self) -> None:
        """returns table colums as Pandas DataFrame"""
        # molgenis.csv column names
        # added columns DataType, FieldType and TextValidationType to later determine the columnType
        self.molgenis_df = pd.DataFrame(
            [],
            columns=[
                'tableName',
                'columnName',
                'columnType',
                'tableExtends',
                'refBack',
                'description',
                'semantics',
                'refLink',
                'refTable',
                'key',
                'required',
                'validation',
                
                'DataType',
                'FieldType',
                'TextValidationType'])
        #return df

    def molgenis_table(self) -> None:
        """Process found tables (instruments) in ODM"""
        # get the table name(s)
        tables = self.attribute_values('.//odm:FormDef', '{https://projectredcap.org}FormName')
        for table in tables:
            # add Form into molgenis
            self.molgenis_df = self.molgenis_df.append({'tableName': table}, ignore_index=True)
            # add SubjectKey as key 1
            self.molgenis_df = self.molgenis_df.append({
                'tableName': table,
                'columnName': 'SubjectKey',
                'columnType': '', 
                'key': '1', 
                'required': 'TRUE'}, ignore_index=True)
            # add FormRepeatKey
            self.molgenis_df = self.molgenis_df.append({
                'tableName': table,
                'columnName': 'FormRepeatKey',
                'columnType': '',
                'key': '',
                'required': ''}, ignore_index=True)

            # for variable
            self.molgenis_variable(table)

    def molgenis_variable(self, table_name: str) -> None:
        """process ItemGroupDef"""
        # get the form variable names
        variable_names = self.attribute_values('.//odm:ItemGroupDef', 'OID')
        for variable_name in variable_names:
                if re.search(table_name, variable_name):
                    # get ItemGroupDef (column) for given variable_name
                    column = Redcap.attributes(self.doc, ".//odm:ItemGroupDef[@OID='"+variable_name+"']/")
                    # for columns
                    self.molgenis_column(column['ItemOID'], table_name)

    def molgenis_column(self, column, table_name: str) -> None:
        """process ItemDef"""
        for column_name in column:
            description = self.attribute_value(".//odm:ItemDef[@OID='"+column_name+"']", '{https://projectredcap.org}FieldNote')
            data_type = self.attribute_value(".//odm:ItemDef[@OID='"+column_name+"']", 'DataType')
            field_type = self.attribute_value(".//odm:ItemDef[@OID='"+column_name+"']", '{https://projectredcap.org}FieldType')
            text_validation_type = self.attribute_value(".//odm:ItemDef[@OID='"+column_name+"']", '{https://projectredcap.org}TextValidationType')

            self.molgenis_df = self.molgenis_df.append({
                'tableName': table_name,
                'columnName': column_name,
                'description': description,
                'DataType': data_type,
                'FieldType': field_type,
                'TextValidationType': text_validation_type
            }, ignore_index=True)
            
    def attribute_values(self, element: str, attribute_name: str) -> np.ndarray:
        """pass element and attribute and retrieve the value(s)"""
        attributes = Redcap.attributes(self.doc, element)
        try:
            values = attributes[attribute_name].values
        except:
            values = False
        return values

    
    def attribute_value(self, element: str, attribute_name: str) -> str:
        """return single value (str) of element or False if attribute name does not exists"""
        i = self.attribute_values(element, attribute_name)
        value = i[0] if i else False
        return value

    def emx2_datatype(self) -> None:
        """Determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
        
        Order of events is important"""
        emx2_datatypes = self.emx2_datatype_list()
        for i in emx2_datatypes:
            if emx2_datatypes[i]['TextValidationType']:
                self.molgenis_df.loc[
                    (self.molgenis_df['DataType'] == emx2_datatypes[i]['DataType']) &
                    (self.molgenis_df['FieldType'] == emx2_datatypes[i]['FieldType']) & 
                    (self.molgenis_df['TextValidationType'] == emx2_datatypes[i]['TextValidationType']), 'columnType'] =  emx2_datatypes[i]['columnType']
            else:
                self.molgenis_df.loc[
                    (self.molgenis_df['DataType'] == emx2_datatypes[i]['DataType']) &
                    (self.molgenis_df['FieldType'] == emx2_datatypes[i]['FieldType']), 'columnType'] =  emx2_datatypes[i]['columnType']

    def emx2_datatype_list(self) -> dict:
        """Defines the columnType for EMX to convert to and return a dictionary
        
        Order is important"""
        dict = {
            1: {'DataType': 'text', 'FieldType': 'text', 'TextValidationType': 'email', 'columnType': 'text'},
            2: {'DataType': 'date', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'date'},
            3: {'DataType': 'partialDatetime', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'datetime'},
            4: {'DataType': 'datetime', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'datetime'},
            5: {'DataType': 'text', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'text'},
            6: {'DataType': 'integer', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'int'},
            7: {'DataType': 'float', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'decimal'},
            8: {'DataType': 'partialTime', 'FieldType': 'text', 'TextValidationType': '', 'columnType': 'string'},
            9: {'DataType': 'text', 'FieldType': 'textarea', 'TextValidationType': '', 'columnType': 'text'},
            10: {'DataType': 'float', 'FieldType': 'calc', 'TextValidationType': '', 'columnType': 'decimal'},
            11: {'DataType': 'text', 'FieldType': 'select', 'TextValidationType': '', 'columnType': 'text'},
            12: {'DataType': 'text', 'FieldType': 'radio', 'TextValidationType': '', 'columnType': 'text'},
            13: {'DataType': 'boolean', 'FieldType': 'checkbox', 'TextValidationType': '', 'columnType': 'text'},
            14: {'DataType': 'boolean', 'FieldType': 'yesno', 'TextValidationType': '', 'columnType': 'bool'},
            15: {'DataType': 'boolean', 'FieldType': 'truefalse', 'TextValidationType': '', 'columnType': 'bool'},
            16: {'DataType': 'text', 'FieldType': 'file', 'TextValidationType': '', 'columnType': 'file'},
            17: {'DataType': 'integer', 'FieldType': 'slider', 'TextValidationType': '', 'columnType': 'int'},
            18: {'DataType': 'text', 'FieldType': 'descriptive', 'TextValidationType': '', 'columnType': 'text'}
        }
        return dict
    
    def molgenis_csv(self) -> None:
        """Build and output a valid molgenis.csv from Pandas DataFrame"""

        # remove REDCap columns DataType, FieldType and TextValidationType
        data = self.molgenis_df.drop(columns=['DataType','FieldType','TextValidationType'])
        data = data.fillna('')
        data.to_csv(r'./data/output/molgenis.csv', index=False, header=True)
        # set self.molgenis_df empty?
    
    def clinical_data(self) -> None:
        """Build and output table data if clinical_data is available"""

        if not self.attribute_value(".//odm:ClinicalData", 'StudyOID'):
            print('No ClinicalData found for this Study.')
            exit(1)
        
        # setup data MultiIndex DataFrame
        columns = pd.MultiIndex.from_frame(self.form_variables())
        index = pd.MultiIndex.from_product([[],[]], names=['SubjectKey','FormRepeatKey'])
        data = pd.DataFrame([], index=index, columns=columns)

        #if not self.attribute_values(".//odm:StudyEventData", 'StudyEventOID'):
        #    print('No repeat')
        
        # determine if repeated measurments are used
        StudyEventData = Redcap.attributes(self.doc, './/odm:StudyEventData')
        
        SubjectKeys = self.attribute_values('.//odm:SubjectData', 'SubjectKey')

        try:
            if StudyEventData == None:
                # No repeated instruments found, get data
                data = self.clinical_data_no_repeats(SubjectKeys, data)
        except ValueError:
            # Repeated instruments, get data
            data = self.clinical_data_repeats(SubjectKeys, data)

        forms = self.get_forms()
        
        for i in forms.index:
            form_name = forms['FormName'][i]
            form_data = data[forms['OID'][i]]
            
            transformed_form_data = self.transform_redcap_boolean(form_data)
            self.data_csv(transformed_form_data, form_name)
    
    def form_variables(self) -> pd.DataFrame:
        """Returns a pandas DataFrame with two columns: FormOID, ItemOID of all Forms used by the Study"""
        forms = self.get_forms()

        subselection_molgenis_df = self.molgenis_df[['tableName','columnName']]
        subselection_molgenis_df = subselection_molgenis_df.dropna(subset=['columnName'])

        form_variables = pd.merge(forms, subselection_molgenis_df, left_on='FormName', right_on='tableName')
        form_variables = form_variables.drop(['FormName'], axis=1)
        form_variables = form_variables.drop(['tableName'], axis=1)

        form_variables.rename(columns={'OID': 'FormOID', 'columnName': 'ItemOID'}, inplace=True)

        return form_variables

    def get_forms(self) -> pd.DataFrame:
        """Returns a pandas DataFrame with to columns: OID, FormName"""
        # determine which forms are included and need to be extracted
        forms = pd.concat([
            pd.Series(self.attribute_values('.//odm:FormDef', 'OID'), name='OID'), 
            pd.Series(self.attribute_values('.//odm:FormDef', '{https://projectredcap.org}FormName'), name='FormName')], axis=1)
        return forms

    def clinical_data_no_repeats(self, SubjectKeys: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
        """Retrieve clinicaldata from study without repeated measurements"""
        for SubjectKey in SubjectKeys:

            SubjectData = Redcap.iterfind(self.doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

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


    def clinical_data_repeats(self, SubjectKeys: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
        """Retrieve clinicaldata from study with repeated measurements"""
        for SubjectKey in SubjectKeys:

            SubjectData = Redcap.iterfind(self.doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

            for i in SubjectData:
                for j in i:
                    for k in j:
                        for l in k:
                            data.loc[(SubjectKey,j.attrib['FormRepeatKey']),
                                ([j.attrib['FormOID']],[l.attrib['ItemOID']])] = l.attrib['Value']
        return data

    def transform_redcap_boolean(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform REDCap bool (0/1) to EMX2 TRUE/FALSE"""
        field_types: list = ['truefalse', 'yesno']
        columns = list(data.columns)

        data_copy = data.copy()

        # see if REDCap variable is defined as boolean
        for column_name in columns:          
            # check if variable (c) is defined as boolean and one of the field_types
            for field_type in field_types:
                row = self.molgenis_df.loc[
                    (self.molgenis_df['DataType'] == 'boolean') & (self.molgenis_df['FieldType'] == field_type) & (self.molgenis_df['columnName'] == column_name)]
                
                if row.index.notnull():
                    data_copy[column_name] = data_copy[column_name].replace(['0'],'FALSE')
                    data_copy[column_name] = data_copy[column_name].replace(['1'],'TRUE')
        return data_copy
    
    def data_csv(self, df: pd.DataFrame, name: str) -> None:
        """Transform DataFrame and write 'data'.csv"""
        # drop columns SubjectKey and FormRepeatKey they are empty 
        # and replaced by multiindex (SubjectKey and FormRepeatKey).
        df = df.drop(['SubjectKey'], axis=1)
        df = df.drop(['FormRepeatKey'], axis=1)
        # drop NaN
        df = df.dropna(how='all')
        df.to_csv(r'./data/output/' + name + '.csv', index=True, header=True)