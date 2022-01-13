'''get instruments, vars, codelist?'''
import pandas as pd

import src.exceptions
import src.cdisc
# from exceptions import NoClinicalData
#from cdisc import Cdisc

def defined_instruments(file: str, namespace: str) -> list:
    '''return list of defined instruments'''
    return src.cdisc.Cdisc.attribute_values(src.cdisc.Cdisc(file, 'REDCap'), './/odm:FormDef', namespace + 'FormName')

def study_contains_clinicaldata(file: str) -> None:
    '''see if REDCap xml contains clinical data, if not exit'''
    if not src.cdisc.Cdisc.attribute_value(src.cdisc.Cdisc(file, 'REDCap'), ".//odm:ClinicalData", 'StudyOID'):
        raise src.exceptions.NoClinicalData

def study_contains_repeating_instrument(file: str, namespace: str) -> bool:
    '''if study contains repeating instrument(s) return True, if not False'''
    i = src.cdisc.Cdisc.attribute_values(src.cdisc.Cdisc(file, 'REDCap'), ".//" + namespace + "RepeatingInstrument", namespace + "RepeatInstrument")
    return (True if i else False)

def study_contains_study_event_data(file: str) -> bool:
    '''if study contains StudyEventData (repeating instrument(s)) return True, if not False'''
    i = src.cdisc.Cdisc.attributes(src.cdisc.Cdisc(file, 'REDCap'), ".//odm:StudyEventData")
    try:
        if i == None:
            return False
    except ValueError:
        return True

def defined_repeating_instruments(file: str, namespace: str) -> set:
    '''return set of repaiting instrument(s)'''
    return set(src.cdisc.Cdisc.attribute_values(src.cdisc.Cdisc(file, 'REDCap'), ".//" + namespace + "RepeatingInstrument", namespace + "RepeatInstrument"))

def subject_keys(file: str) -> set:
    '''subject keys defined by REDCap returned as set'''
    return set(src.cdisc.Cdisc.attribute_values(src.cdisc.Cdisc(file, 'REDCap'), './/odm:SubjectData', 'SubjectKey'))

def form_repeat_keys(file: str) -> set:
    '''FormRepeatKeys defined by REDCap returned as set'''
    return set(src.cdisc.Cdisc.attribute_values(src.cdisc.Cdisc(file, 'REDCap'), './/odm:FormData', 'FormRepeatKey'))

def subject_data_table_keys(file: str) -> list:
    '''format keys: SubjectKey_FormRepeatKey and return list'''
    return [f'{j}_{y}' for i, j in enumerate(subject_keys(file)) for x, y in enumerate(form_repeat_keys(file))]

def subject_data_table_subject_keys(file: str) -> list:
    '''format subject keys: SubjectKey and return as list
    
    Making sure to return the correct number of SubjectKeys'''
    return [f'{j}' for i, j in enumerate(subject_keys(file)) for x, y in enumerate(form_repeat_keys(file))]

def subject_data_table_form_repeat_keys(file: str) -> list:
    '''format form repeat keys: FormRepeatKey and return as list
    
    Making sure to return the correct number of FormRepeatKeys'''
    return [f'{y}' for i, j in enumerate(subject_keys(file)) for x, y in enumerate(form_repeat_keys(file))]

def datamodel_table_columns() -> pd.DataFrame:
    '''returns (empty) datamodel aka molgenis.csv table with column names
    
    added the following REDCap columns to determine the (emx2) columnType: DataType, FieldType and TextValidationType'''
    result = pd.DataFrame([],
        columns=[
            'tableName', 'columnName', 'columnType', 'tableExtends',
            'refBack', 'description', 'semantics', 'refLink',
            'refTable', 'key', 'required', 'validation',
            'DataType', 'FieldType', 'TextValidationType']
    )
    return result