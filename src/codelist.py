'''codelists'''
from abc import ABC, abstractmethod

import src.exceptions
import src.REDCap.codelist
import src.REDCap.utils
# from exceptions import NoValidEdc
# from REDCap.codelist import REDCapCodelist
# from REDCap.utils import study_contains_clinicaldata

class Codelist(ABC):

    def __init__(self, edc: str, file: str) -> None:
        self.edc = edc
        self.file = file
        super().__init__()

    @abstractmethod
    def execute(self) -> None:
        pass

class Variables(Codelist):

    def execute(self) -> None:
        print(f"Variables, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            src.REDCap.codelist.REDCapCodelist(self.file).codelist_data_table()
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

class VariableValues(Codelist):

    def execute(self) -> None:
        print(f"RepeatedVariables, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            pass
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

def codelists(edc, file) -> None:
    src.REDCap.utils.study_contains_clinicaldata(file)

    Variables(edc, file).execute()
    VariableValues(edc, file).execute()