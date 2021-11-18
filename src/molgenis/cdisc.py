import re
import xml.etree.ElementTree as ET
import pandas as pd
import sys

class Cdisc:
    
    def __init__(self, file: str, edc: str='REDCap') -> None:
        self.file = file
        self.read_parse_xml(file)
        self.namespace(edc)
        #self.namespaces = {'odm': self.namespace}
        self.namespaces = {'odm': self.namespace, 'redcap': 'https://projectredcap.org'}
    
    def read_parse_xml(self, file: str) -> ET.ElementTree:
        '''Read and parse xml'''
        try:
            # register namespace
            ET.register_namespace("redcap", "https://projectredcap.org")
            print('Parsing file: ' + file)
            self.root = ET.parse(file).getroot()
        except FileNotFoundError:
            sys.exit('File not found, please give correct file path.')
        except ET.ParseError:
            sys.exit('ParseError, please provide valid xml file.')

    def namespace(self, edc: str) -> str:
        '''Return the namespace uri for the current file'''
        # note that this is the *module*'s `register_namespace()` function
        #ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
        print('Electronic Data Capture (EDC) system: '+ edc)
        try:
            self.namespace = re.compile(r'\{(.+)\}').match(self.root.tag).group(1)
        except:
            sys.exit('Failed to retrieve namespace.')
    
    def attributes(self, xpath: str) -> pd.DataFrame:
        '''Returns Pandas DataFrame of found attributes'''
        columns = self.root.find(xpath, self.namespaces)
        if columns is not None:

            return pd.DataFrame(
                [i.attrib for i in self.root.findall(xpath, self.namespaces)], columns=list(columns.attrib))

        return None


    def attribute_values(self, element: str, name: str) -> pd.DataFrame:
        '''pass element and attribute and retrieve the value(s'''
        attributes = self.attributes(element)
        try:
            values = attributes[name].values
        except:
            values = False
        return values

    def attribute(self, xpath: str) -> pd.DataFrame:
        '''Returns Pandas DataFrame of found attribute'''
        columns = self.root.find(xpath, self.namespaces)
        if columns is not None:
            return pd.DataFrame([self.root.find(xpath, self.namespaces).attrib], columns=list(columns.attrib))
        else:
            return None

    def attribute_value(self, element: str, name: str) -> pd.DataFrame:
        '''return single value of element or False if attribute name does not exists'''
        if value := self.attribute_values(element, name):
            #print(type(value))
            return value[0]
        return None

    def iterfind(self, xpath: str) -> ET.ElementTree:
        '''return tree'''
        return self.root.iterfind(xpath, self.namespaces)