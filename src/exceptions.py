
class Error(Exception):
    pass

class NoValidEdc(Error):

    def __init__(self) -> None:
        self.message = 'No Electronic Data Capture (EDC), select REDCap or Castor.'
        super().__init__()
    
    def __str__(self):
        return f'{self.message}'

class NoFile(Error):
    def __init__(self) -> None:
        self.message = 'No file.'
        super().__init__()
    
    def __str__(self):
        return f'{self.message}'

class ErrorWritingCsv(Error):
    def __init__(self) -> None:
        self.message = 'Could not write output csv'
        super().__init__()
    
    def __str__(self):
        return f'{self.message}'

class NoClinicalData(Error):
    def __init__(self) -> None:
        self.message = 'No ClinicalData found for this Study, exiting.'
        super().__init__()
    
    def __str__(self):
        return f'{self.message}'