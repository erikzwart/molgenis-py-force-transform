'''instrument variables and repeatedVariables'''
from abc import ABC, abstractmethod

import src.exceptions
import src.REDCap.instrument
import src.REDCap.utils
#from exceptions import NoValidEdc
#from REDCap.instrument import REDCapInstrument
#from REDCap.utils import study_contains_clinicaldata

class Instrument(ABC):
    
    def __init__(self, edc: str, file: str) -> None:
        self.edc = edc
        self.file = file
        super().__init__()
    
    @abstractmethod
    def execute(self) -> None:
        pass

class SubjectData(Instrument):

    def execute(self) -> None:
        print(f"Subjects, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            src.REDCap.instrument.REDCapInstrument(self.file).subject_data_table()
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

class Variables(Instrument):

    def execute(self) -> None:
        print(f"Intrument variables, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            src.REDCap.instrument.REDCapInstrument(self.file).instrument_data_table()
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

def instruments(edc, file) -> None:
    src.REDCap.utils.study_contains_clinicaldata(file)
    
    SubjectData(edc, file).execute()
    Variables(edc, file).execute()