import configparser
import pathlib

from enum import Enum

import src.exceptions
import src.export
import src.datamodel
import src.instrument
import src.codelist


class Edc(Enum):
    '''Electronic Data Capture (EDC)'''
    REDCAP = 'REDCap'
    CASTOR = 'Castor'
    DUMMY = 'Dummy'

class Transform():
    '''Electronic Data Capture (EDC): REDCAP, CASTOR(not implemented), file: CDISC ODM (xml)'''
    def __init__(self, edc: None = None, file: str = None) -> None:

        config = configparser.ConfigParser()
        config.read('src/config.ini')

        if file is None:
            raise src.exceptions.NoFile()
        
        file = pathlib.Path().joinpath(config['settings']['input_folder'],file)

        if not file.is_file():
            raise src.exceptions.NoFile()
        
        output_folder = pathlib.Path().joinpath(config['settings']['output_folder'])
        src.export.export.is_dir(output_folder)
        src.export.export.is_empty(output_folder)

        if (edc not in Edc._value2member_map_):
            raise src.exceptions.NoValidEdc()

        print(f'Running {edc}')
        print(f'Processing {file}')
        print('**data model**')
        src.datamodel.datamodel(edc, file)
        print('**instruments**')
        src.instrument.instruments(edc, file)
        print('**codelists**')
        src.codelist.codelists(edc, file)

if __name__ == '__main__':
    Transform(edc = 'REDCap', file = 'Example_1_REDCap_meta.xml')
    #Transform(edc = 'REDCap', file = 'Example_2_REDCap_repeated-measures.xml')
    #Transform(edc = 'REDCap', file = 'Example_3_TestHumanCancer_REDCap.xml')
    #Transform(edc = 'REDCap', file = 'Example_5_missing-clinical-data.xml')
    #Transform(edc = Edc.CASTOR, file = 'testC.xml')
    #Transform(edc = Edc.DUMMY, file = 'test.xml')
    #Transform(edc = 'REDCap', file='test.xml')
    #Transform(edc = 'REDCap', file=None)

