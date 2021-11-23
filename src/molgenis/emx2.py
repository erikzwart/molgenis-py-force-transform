import pandas as pd
import sys

from pathlib import Path

class Molgenis:

    def table_columns() -> pd.DataFrame:
        '''returns (empty) Molgenis table with column names as Pandas DataFrame
        
        create empty molgenis.csv and add columns
        - added the following extra columns to be able to determine columnType
          DataType
          FieldType
          TextValidationType'''
        df = pd.DataFrame(
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
                'TextValidationType']
        )
        return df

    def instrument_table(df: pd.DataFrame, instrument: str) -> pd.DataFrame:
        '''Append instrument names to molgenis.csv pandas DataFrame
        
        append instrument (tables) to molgenis.csv'''
        # add instrument as table into molgenis
        df = df.append({'tableName': instrument}, ignore_index=True)
        # add key that is the combination of SubjectKey and FormRepeatKey
        df = df.append({
            'tableName': instrument,
            'columnName': 'key',
            'columnType': 'ref',
            'refTable': 'SubjectData',
            'key': '1', 
            'required': 'TRUE'}, ignore_index=True)

        # add SubjectKey as key 1
        df = df.append({
            'tableName': instrument,
            'columnName': 'SubjectKey',
            'columnType': '', 
            'key': '', 
            'required': 'TRUE'}, ignore_index=True)

        # add FormRepeatKey
        df = df.append({
            'tableName': instrument,
            'columnName': 'FormRepeatKey',
            'columnType': '',
            'key': '',
            'required': ''}, ignore_index=True)

        return df

    def variable_table(df: pd.DataFrame, data = list) -> pd.DataFrame:
        '''Add variable data to molgenis.csv pandas DataFrame'''
        df = df.append({
            'tableName': data[0],
            'columnName': data[1],
            'description': data[2],
            'DataType': data[3],
            'FieldType': data[4],
            'TextValidationType': data[5]
        }, ignore_index=True)
        return df
    
    def subjectData_table(SubjectKeys: list, FormRepeatKeys: list, path: str, file: str) -> None:
        '''setup SubjectData table, contains the keys that is a combination of SubjectKey and FormRepeatKey (1_1, 1_2 ..)'''

        x = int(max(SubjectKeys))
        y = int(max(FormRepeatKeys))

        keys = [ ["_".join([str(i), str(j)])] for i in range(1, x + 1) for j in range(1, y + 1)]
        keys = [y for x in keys for y in x] # flatten the list of lists
        allSubjectKeys = [int(i[1]) for i in enumerate(SubjectKeys) for j in range(1, y + 1)]
        allFormRepeatKeys = [j for i in enumerate(SubjectKeys) for j in range(1, y +1)]

        df = pd.DataFrame({
            'key': keys,
            'SubjectKey': allSubjectKeys,
            'FormRepeatKey': allFormRepeatKeys
        })

        try:
            print('Writing ' + file)
            df.to_csv(Path(path + file), index=False, header=True)
        except:
            sys.exit('Writing ' + file + ' failed, exiting.')


    def write_molgenis_csv(df: pd.DataFrame, path: str, file: str) -> None:
        '''Transform and output a valid molgenis.csv from Pandas DataFrame'''
        # remove REDCap columns DataType, FieldType and TextValidationType
        data = df.drop(columns=['DataType','FieldType','TextValidationType'])
        # remove rows with columnType == SubjectKey and FormRepeatKey
        data = data[data.columnName != 'SubjectKey']
        data = data[data.columnName != 'FormRepeatKey']

        # add SubjectData table
        data = data.append({'tableName': 'SubjectData'}, ignore_index=True)
        data = data.append({
            'tableName': 'SubjectData',
            'columnName': 'key',
            'key': '1', 
            'required': 'TRUE'}, ignore_index=True)
        data = data.append({
            'tableName': 'SubjectData',
            'columnName': 'SubjectKey',
            'required': 'TRUE'}, ignore_index=True)
        data = data.append({
            'tableName': 'SubjectData',
            'columnName': 'FormRepeatKey',
            'required': 'TRUE'}, ignore_index=True)
        # fill NaN values with ''
        data = data.fillna('')
        #print(data)
        try:
            print('Writing ' + file)
            data.to_csv(Path(path + file), index=False, header=True)
        except:
            sys.exit('Writing ' + file + ' failed, exiting.')
    
    def write_instrument_csv(
        df: pd.DataFrame, 
        path: str, 
        instrument: str,
        repeating: bool = False) -> None:
        '''Transform DataFrame and write 'instrument'.csv'''
        # drop columns SubjectKey and FormRepeatKey they are empty 
        # and replaced by multiindex (SubjectKey and FormRepeatKey).

        data = df.copy()
        
        if 'SubjectKey' in data:
            data.drop(['SubjectKey'], axis=1, inplace=True)
            data.drop(['FormRepeatKey'], axis=1, inplace=True)
            data.drop(['key'], axis=1, inplace=True)
        
        #data.drop(['key'], axis=1, inplace=True)

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
            print('Writing ' + instrument + '.csv')
            data.to_csv(Path(path + instrument + '.csv'), index=False, header=True)
        except:
            sys.exit('Writing ' + instrument + '.csv failed, exiting.')

class Emx2:

    def datatype(df: pd.DataFrame) -> pd.DataFrame:
        '''Determine the emx2 datatype based on REDCAP DataType, FieldType and TextValidationType
        
        Order of events is important'''
        emx2_datatypes = Emx2.__datatype_list()
        for i in emx2_datatypes:
            if emx2_datatypes[i]['TextValidationType']:
                df.loc[
                    (df['DataType'] == emx2_datatypes[i]['DataType']) &
                    (df['FieldType'] == emx2_datatypes[i]['FieldType']) & 
                    (df['TextValidationType'] == emx2_datatypes[i]['TextValidationType']), 'columnType'] =  emx2_datatypes[i]['columnType']
            else:
                df.loc[
                    (df['DataType'] == emx2_datatypes[i]['DataType']) &
                    (df['FieldType'] == emx2_datatypes[i]['FieldType']), 'columnType'] =  emx2_datatypes[i]['columnType']
        return df
    
    def __datatype_list() -> dict:
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
            13: {'DataType': 'boolean', 'FieldType': 'checkbox', 'TextValidationType': '', 'columnType': 'text'},
            14: {'DataType': 'boolean', 'FieldType': 'yesno', 'TextValidationType': '', 'columnType': 'bool'},
            15: {'DataType': 'boolean', 'FieldType': 'truefalse', 'TextValidationType': '', 'columnType': 'bool'},
            16: {'DataType': 'text', 'FieldType': 'file', 'TextValidationType': '', 'columnType': 'file'},
            17: {'DataType': 'integer', 'FieldType': 'slider', 'TextValidationType': '', 'columnType': 'int'},
            18: {'DataType': 'text', 'FieldType': 'descriptive', 'TextValidationType': '', 'columnType': 'text'}
        }
        return dict