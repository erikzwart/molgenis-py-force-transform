'''Get data from REDCap CDISC ODM and convert to instrument tables'''
import configparser
import numpy as np
import pandas as pd
import sys

import src.cdisc
import src.export
import src.REDCap.datamodel
import src.REDCap.utils
#from REDCap.utils import defined_instruments, defined_repeating_instruments, study_contains_repeating_instrument, subject_keys, form_repeat_keys, subject_data_table_keys, subject_data_table_subject_keys, subject_data_table_form_repeat_keys, study_contains_study_event_data
#from REDCap.datamodel import REDCapDatamodel
#from cdisc import Cdisc
#from export import export


class REDCapInstrument():
    config = configparser.ConfigParser()
    config.read('./src/config.ini')
    
    ns = config['redcap']['namespace']
    output_folder = config['settings']['output_folder']
    subject_data_csv = config['settings']['subject']
    subject_data_name = config['settings']['subject'].split(".")[0]

    def __init__(self, file: str) -> None:
        self.file = file

    def subject_data_table(self) -> None:
        '''setup SubjectData table, contains the keys that is a combination of SubjectKey and FormRepeatKey (1_1, 1_2 ..)'''
        def subject_data_table_dataframe(self) -> pd.DataFrame:
            '''combine keys, subject keys and form repeat keys and return SubjectData pd.dataframe'''
            return pd.DataFrame({
                'key': src.REDCap.utils.subject_data_table_keys(self.file),
                'SubjectKey': src.REDCap.utils.subject_data_table_subject_keys(self.file),
                'FormRepeatKey': src.REDCap.utils.subject_data_table_form_repeat_keys(self.file)
            })

        src.export.export.instrument_to_csv(subject_data_table_dataframe(self), self.subject_data_csv)

    def instrument_data_table(self) -> None:
        '''retrieve instrument data'''
        xml = src.cdisc.Cdisc(self.file, 'REDCap')

        #instruments = defined_instruments(self.file, self.ns)
        
        def get_forms(self) -> pd.DataFrame:
            '''Returns a pandas DataFrame with to columns: OID, FormName'''
            # determine which forms are included and need to be extracted
            return pd.concat([
                pd.Series(src.cdisc.Cdisc.attribute_values(xml, './/odm:FormDef', 'OID'), name='OID'), 
                pd.Series(src.cdisc.Cdisc.attribute_values(xml, './/odm:FormDef', self.ns + 'FormName'), name='FormName')], axis=1)
        
        def form_variables(self, dataframe: pd.DataFrame) -> pd.DataFrame:
            '''Returns a pandas DataFrame with two columns: FormOID, ItemOID of all Forms used by the Study'''
            df = dataframe[['tableName','columnName']]
            df = df.dropna(subset=['columnName'])

            v = pd.merge(get_forms(self), df, left_on='FormName', right_on='tableName')
            v = v.drop(['FormName'], axis=1)
            v = v.drop(['tableName'], axis=1)

            v.rename(columns={'OID': 'FormOID', 'columnName': 'ItemOID'}, inplace=True)

            return v
        
        def dataframe_multiindex():
            '''setup data MultiIndex DataFrame'''
            dataframe = src.REDCap.datamodel.REDCapDatamodel.generate_instruments(self, to_csv = False, to_dataframe = True)
            columns = pd.MultiIndex.from_frame(form_variables(self, dataframe))
            index = pd.MultiIndex.from_product([[],[]], names=['SubjectKey','FormRepeatKey'])
            return pd.DataFrame([], index=index, columns=columns)

        def clinical_data_no_repeats(subject_keys: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
            '''Retrieve clinicaldata from study without repeated measurements'''
            for SubjectKey in subject_keys:

                SubjectData = src.cdisc.Cdisc.iterfind(xml, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

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

        def clinical_data_repeats(subject_keys: np.ndarray, data: pd.DataFrame) -> pd.DataFrame:
            '''Retrieve clinicaldata from study with repeated measurements'''
            for SubjectKey in subject_keys:

                SubjectData = src.cdisc.Cdisc.iterfind(xml, ".//odm:SubjectData[@SubjectKey='"+SubjectKey+"']/")

                for i in SubjectData:
                    for j in i:
                        for k in j:
                            for l in k:
                                data.loc[(SubjectKey,j.attrib['FormRepeatKey']),
                                    ([j.attrib['FormOID']],[l.attrib['ItemOID']])] = l.attrib['Value']
            return data
      
        def transform_redcap_boolean(instrument_data: pd.DataFrame) -> pd.DataFrame:
            '''Transform REDCap bool (0/1) to EMX2 TRUE/FALSE'''
            df = src.REDCap.datamodel.REDCapDatamodel.generate_instruments(self, to_csv = False, to_dataframe = True)
            
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
            
        def write_instrument_csv(dataframe: pd.DataFrame, instrument: str, repeating: bool = False) -> None:
            '''Transform DataFrame and write 'instrument'.csv'''
            # drop columns SubjectKey and FormRepeatKey they are empty 
            # and replaced by multiindex (SubjectKey and FormRepeatKey).

            data = dataframe.copy()
            
            if 'SubjectKey' in data:
                data.drop(['SubjectKey'], axis=1, inplace=True)
                data.drop(['FormRepeatKey'], axis=1, inplace=True)
                data.drop(['key'], axis=1, inplace=True)

            # make sure each row has correct SubjectKey and FormRepeatKey
            index = pd.DataFrame(
                [keys for keys in data.index.values],
                columns=['SubjectKey','FormRepeatKey']
            )

            repeatKey = index['SubjectKey'] + "_" + index['FormRepeatKey']
            nonRepeatKey = index['SubjectKey'].unique() + "_1"

            # insert SubjectKey and FormRepeatKey to instrument
            # if instrument has no repeated measurements only use the first FormRepeatKey
            # if instrument has repeated measures, add all FormRepeatKey(s)
            if repeating:
                data.dropna(how='all', inplace=True)
                data.insert(0, 'key', repeatKey.to_list())
            else:
                data.dropna(how='all', inplace=True)
                data.reset_index(drop=True, inplace=True)
                data.insert(0, 'key', nonRepeatKey.tolist())
            try:
                print(f'Writing {instrument}.csv')
                src.export.export.instrument_to_csv(data, f'{instrument}.csv')
            except:
                sys.exit(f'Writing {instrument}.csv failed, exiting.')
        
        if src.REDCap.utils.study_contains_study_event_data(self.file):
            clinical_data = clinical_data_repeats(src.REDCap.utils.subject_keys(self.file), dataframe_multiindex())
        else:
            clinical_data = clinical_data_no_repeats(src.REDCap.utils.subject_keys(self.file), dataframe_multiindex())

        instruments = get_forms(self)
        
        for i in instruments.index:
            instrument_name = instruments['FormName'][i]
            instrument_data = clinical_data[instruments['OID'][i]]
            transformed_clinical_data = transform_redcap_boolean(instrument_data)

            if src.REDCap.utils.study_contains_repeating_instrument(self.file, self.ns):
                if instrument_name in src.REDCap.utils.defined_repeating_instruments(self.file, self.ns):
                    write_instrument_csv(transformed_clinical_data, instrument_name, True)
            else:
                write_instrument_csv(transformed_clinical_data, instrument_name, False)