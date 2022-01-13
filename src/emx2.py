'''convert to emx2 datatypes'''
import pandas as pd

class Emx2:

    def REDCap_datatype(dataframe: pd.DataFrame) -> pd.DataFrame:
        '''Determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
        
        Order of events is important'''
        def datatype_list() -> dict:
            '''Defines the columnType for EMX to convert to and return a dictionary
            
            Order is important'''
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
                13: {'DataType': 'boolean', 'FieldType': 'checkbox', 'TextValidationType': '', 'columnType': 'ref_array'},
                14: {'DataType': 'boolean', 'FieldType': 'yesno', 'TextValidationType': '', 'columnType': 'ref'},
                15: {'DataType': 'boolean', 'FieldType': 'truefalse', 'TextValidationType': '', 'columnType': 'ref'},
                16: {'DataType': 'text', 'FieldType': 'file', 'TextValidationType': '', 'columnType': 'file'},
                17: {'DataType': 'integer', 'FieldType': 'slider', 'TextValidationType': '', 'columnType': 'int'},
                18: {'DataType': 'text', 'FieldType': 'descriptive', 'TextValidationType': '', 'columnType': 'text'}
            }
            return dict

        datatypes = datatype_list()
        
        for i in datatypes:
            if datatypes[i]['TextValidationType']:
                dataframe.loc[
                    (dataframe['DataType'] == datatypes[i]['DataType']) &
                    (dataframe['FieldType'] == datatypes[i]['FieldType']) & 
                    (dataframe['TextValidationType'] == datatypes[i]['TextValidationType']), 'columnType'] =  datatypes[i]['columnType']
            else:
                dataframe.loc[
                    (dataframe['DataType'] == datatypes[i]['DataType']) &
                    (dataframe['FieldType'] == datatypes[i]['FieldType']), 'columnType'] =  datatypes[i]['columnType']
        return dataframe