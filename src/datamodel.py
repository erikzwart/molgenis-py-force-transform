'''aka molgenis.csv'''
from abc import ABC, abstractmethod

import src.exceptions
import src.REDCap.datamodel
import src.REDCap.utils
#from exceptions import NoValidEdc
#from REDCap.datamodel import REDCapDatamodel
#from REDCap.utils import study_contains_clinicaldata

class Molgenis(ABC):

    def __init__(self, edc: str, file: str) -> None:
        self.edc = edc
        self.file = file
        super().__init__()

    @abstractmethod
    def execute(self) -> None:
        pass

class SubjectData(Molgenis):

    def execute(self) -> None:
        print(f"Subjects, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            src.REDCap.datamodel.REDCapDatamodel(self.file).subject_data()
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

class Instruments(Molgenis):

    def execute(self) -> None:
        print(f"Intruments, EDC: {self.edc}, file: {self.file}")
        if self.edc == 'REDCap':
            src.REDCap.datamodel.REDCapDatamodel(self.file).instruments()
        elif self.edc == 'Castor':
            pass
        else:
            raise src.exceptions.NoValidEdc

def datamodel(edc, file) -> None:
    src.REDCap.utils.study_contains_clinicaldata(file)

    SubjectData(edc, file).execute()
    Instruments(edc, file).execute()