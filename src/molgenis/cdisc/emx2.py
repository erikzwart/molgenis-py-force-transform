import re
import pandas as pd
import numpy as np

from src.molgenis.cdisc.odm import Redcap

class Transform:
    """Transform CDISC ODM to EMX2"""

    def __init__(self, file):
        self.doc = Redcap(file)

        self.molgenis(self.doc)
        self.molgenisTable(self.doc)

    def molgenis(self, doc):
        """Make molgenis.csv"""

        # molgenis.csv column names
        # added columns DataType, FieldType and TextValidationType to later determine the columnType
        df = pd.DataFrame([],columns=['tableName','columnName','columnType',
        'tableExtends','refBack','description','semantics','refLink','refTable',
        'key','required','validation','DataType','FieldType','TextValidationType'])

        FormDef = Redcap.attributes(doc, './/odm:FormDef')
        ItemGroupDef = Redcap.attributes(doc, './/odm:ItemGroupDef')
        
        FormNames =  FormDef['{https://projectredcap.org}FormName'].values
        ItemGroupDefOIDs = ItemGroupDef['OID'].values

        # Need to add record_id or SubjectKey to every table and make sure it is a key (add own unique key to make it work..)
        
        for FormName in FormNames:
            # add Form into molgenis
            df = df.append({'tableName': FormName}, ignore_index=True)
            # add SubjectKey as key 1
            df = df.append({'tableName': FormName, 'columnName': 'SubjectKey', 'columnType': '', 'key': '1', 'required': 'TRUE'}, ignore_index=True)
            # add FormRepeatKey
            #df = df.append({'tableName': FormName, 'columnName': 'FormRepeatKey', 'columnType': '', 'key': '2', 'required': 'TRUE'}, ignore_index=True)
            df = df.append({'tableName': FormName, 'columnName': 'FormRepeatKey', 'columnType': '', 'key': '', 'required': ''}, ignore_index=True)
            for ItemGroupDefOID in ItemGroupDefOIDs:
                if re.search(FormName, ItemGroupDefOID):

                    ItemRef = Redcap.attributes(doc, ".//odm:ItemGroupDef[@OID='"+ItemGroupDefOID+"']/")

                    for ItemOID in ItemRef['ItemOID']:
                        ItemDef = Redcap.attribute(doc, ".//odm:ItemDef[@OID='"+ItemOID+"']")

                        # See if a FieldNote is defined                        
                        ItemDefText = np.nan
                        try:
                            ItemDefText = ItemDef['{https://projectredcap.org}FieldNote'].values[0]
                        except KeyError:
                            pass
                        
                        # See if a TextValidationType is set
                        TextValidationType = np.nan
                        try:
                            TextValidationType = ItemDef['{https://projectredcap.org}TextValidationType'].values[0]
                        except KeyError:
                            pass

                        df = df.append({
                            'tableName': FormName,
                            'columnName': ItemOID,
                            'description': ItemDefText,
                            'DataType': ItemDef['DataType'].values[0],
                            'FieldType': ItemDef['{https://projectredcap.org}FieldType'].values[0],
                            'TextValidationType': TextValidationType
                        }, ignore_index=True)

        self.molgenisDataFrame = self.emx2Datatype(df)
        self.molgenisCsv(self.molgenisDataFrame)
    
    def emx2Datatype(self, df):
        """Determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType"""

        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'text') & (df['TextValidationType'] == 'email'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'date') & (df['FieldType'] == 'text'), 'columnType'] =  'date'
        df.loc[(df['DataType'] == 'partialDatetime') & (df['FieldType'] == 'text'), 'columnType'] =  'datetime'
        df.loc[(df['DataType'] == 'datetime') & (df['FieldType'] == 'text'), 'columnType'] =  'datetime'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'text'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'integer') & (df['FieldType'] == 'text'), 'columnType'] =  'int'
        df.loc[(df['DataType'] == 'float') & (df['FieldType'] == 'text'), 'columnType'] =  'decimal'
        df.loc[(df['DataType'] == 'partialTime') & (df['FieldType'] == 'text'), 'columnType'] =  'string'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'textarea'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'float') & (df['FieldType'] == 'calc'), 'columnType'] =  'decimal'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'select'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'radio'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'boolean') & (df['FieldType'] == 'checkbox'), 'columnType'] =  'text'
        df.loc[(df['DataType'] == 'boolean') & (df['FieldType'] == 'yesno'), 'columnType'] =  'bool'
        df.loc[(df['DataType'] == 'boolean') & (df['FieldType'] == 'truefalse'), 'columnType'] =  'bool'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'file'), 'columnType'] =  'file'
        df.loc[(df['DataType'] == 'integer') & (df['FieldType'] == 'slider'), 'columnType'] =  'int'
        df.loc[(df['DataType'] == 'text') & (df['FieldType'] == 'descriptive'), 'columnType'] =  'text'

        return df
    
    def molgenisCsv(self, df):
        """Build and output a valid molgenis.csv from Pandas DataFrame"""

        # remove REDCap columns DataType, FieldType and TextValidationType
        df = df.drop(columns=['DataType','FieldType','TextValidationType'])
        df = df.fillna('')
        df.to_csv(r'./data/output/molgenis.csv', index=False, header=True)

    def molgenisTable(self, doc):
        """Build and output table data if ClinicalData is available"""
        ClinicalData = Redcap.attribute(doc, './/odm:ClinicalData')
        try:
            ClinicalData['StudyOID']
        except:
            print('No ClinicalData found for this Study.')
            return
        
        # determine how many SubjectKey(s) there are
        SubjectData = Redcap.attributes(doc, './/odm:SubjectData')
        SubjectKeys = SubjectData['SubjectKey'].values

        # determine which forms are included and need to be extracted
        FormDef = Redcap.attributes(doc, './/odm:FormDef')
        
        forms = pd.concat([
            pd.Series(FormDef['OID'].values, name='OID'), 
            pd.Series(FormDef['{https://projectredcap.org}FormName'].values, name='FormName')],
            axis=1)
  
        df = self.molgenisDataFrame[['tableName','columnName']]
        df = df.dropna(subset=['columnName'])
        
        df = pd.merge(forms, df, left_on='FormName', right_on='tableName')

        # repurpose forms
        forms = df[['OID','tableName']]

        forms = pd.concat([
            pd.Series(forms['OID'].unique(), name='FormOID'),
            pd.Series(forms['tableName'].unique(), name='tableName')
        ], axis=1)

        #print(forms)

        df = df.drop(['FormName'], axis=1)
        df = df.drop(['tableName'], axis=1)
        df.rename(columns={'OID': 'FormOID', 'columnName': 'ItemOID'}, inplace=True)

        #print(df)
        # setup data DataFrame
        columns = pd.MultiIndex.from_frame(df)
        index = pd.MultiIndex.from_product([[],[]], names=['SubjectKey','FormRepeatKey'])
        data = pd.DataFrame([], index=index, columns=columns)
        #print(data)

        # determine if repeated measurments are used
        StudyEventData = Redcap.attributes(doc, './/odm:StudyEventData')
        
        try:
            if StudyEventData == None:
                # No repeated instruments found, get data
                data = self.clinicalData(SubjectKeys, doc, data)
        except ValueError:
            # Repeated instruments, get data
            data = self.clinicalDataRepeats(SubjectKeys, doc, data)

        for i in forms.index:
            name = forms['tableName'][i]
            copyData = data[forms['FormOID'][i]]
            
            copyData = self.transformRedcapBool(copyData)
            self.dataCsv(copyData, name)

    def clinicalData(self, SubjectKeys, doc, data):
        """Retrieve clinicalData from study without repeated measurements"""
        for SubjectKey in SubjectKeys:

            SubjectData = Redcap.iterfind(doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

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

    def clinicalDataRepeats(self, SubjectKeys, doc, data):
        """Retrieve clinicalData from study with repeated measurements"""
        for SubjectKey in SubjectKeys:

            SubjectData = Redcap.iterfind(doc, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

            for i in SubjectData:
                for j in i:
                    for k in j:
                        for l in k:
                            data.loc[(SubjectKey,j.attrib['FormRepeatKey']),
                                ([j.attrib['FormOID']],[l.attrib['ItemOID']])] = l.attrib['Value']
        return data

    def transformRedcapBool(self, data):
        """Transform REDCap bool (0/1) to EMX2 TRUE/FALSE"""
        da = data.copy()
        df = self.molgenisDataFrame
        columns = list(da.columns)
        # see if REDCap variable is defined as boolean
        for c in columns:
            # check if variable (c) is defined as boolean and truefalse
            try:
                row = df.loc[(df['DataType'] == 'boolean') 
                    & (df['FieldType'] == 'truefalse') 
                    & (df['columnName'] == c)]
                    
                if row.index.notnull():
                    da[c] = da[c].replace(['0'],'FALSE')
                    da[c] = da[c].replace(['1'],'TRUE')
            except KeyError:
                pass
            # check if variable (c) is defined as boolean and yesno
            try:
                row = df.loc[(df['DataType'] == 'boolean') 
                    & (df['FieldType'] == 'yesno') 
                    & (df['columnName'] == c)]

                if row.index.notnull():
                    da[c] = da[c].replace(['0'],'FALSE')
                    da[c] = da[c].replace(['1'],'TRUE')       
            except KeyError:
                pass
       
        return da

    def dataCsv(self, df, instrumentName):
        """Transform DataFrame and write 'data'.csv"""
        # drop columns SubjectKey and FormRepeatKey they are empty 
        # and replaced by multiindex (SubjectKey and FormRepeatKey).
        df = df.drop(['SubjectKey'], axis=1)
        df = df.drop(['FormRepeatKey'], axis=1)
        # drop NaN
        df = df.dropna(how='all')
        df.to_csv(r'./data/output/' + instrumentName + '.csv', index=True, header=True)