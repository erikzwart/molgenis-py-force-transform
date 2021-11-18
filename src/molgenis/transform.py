import sys
from src.molgenis.redcap import REDCap

class Transform:
    '''Transform CDISC ODM file from Electronic Data Capture (EDC) system like REDCap to MOLGENIS EMX2 format
    '''
    def __init__(self, file: str, edc: str = 'REDCap') -> None:
        if edc == 'REDCap':
            REDCap.main(self, file, edc)
        else:
            print('Electronic Data Capture system not set or unknown: ' + edc)
            sys.exit('Supported EDC: (REDCap,..), exiting.')
