import re
import xml.etree.ElementTree as ET
import pandas as pd
import sys

class Cdisc:
    
    def __init__(self, file: str, edc: str='REDCap') -> None:
        self.file = file
        self.edc = edc
        self.read_parse_xml()
        self.namespace()
        #self.namespaces = {'odm': self.namespace}
        self.namespaces = {'odm': self.namespace, 'redcap': 'https://projectredcap.org'}
    
    def read_parse_xml(self) -> ET.ElementTree:
        '''Read and parse xml'''
        try:
            # register namespace
            # TODO check if register_namespace does anything
            ET.register_namespace("redcap", "https://projectredcap.org")
            #print(f'Parsing file: {self.file}')
            self.root = ET.parse(self.file).getroot()
        except FileNotFoundError:
            sys.exit('File not found, please give correct file path.')
        except ET.ParseError:
            sys.exit('ParseError, please provide valid xml file.')

    def namespace(self) -> str:
        '''Return the namespace uri for the current file'''
        #print(f'Electronic Data Capture (EDC) system: {self.edc}')
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
            return value[0]
        return None

    def iterfind(self, xpath: str) -> ET.ElementTree:
        '''return tree'''
        return self.root.iterfind(xpath, self.namespaces)
    
    def element_text(self, xpath: str) -> pd.DataFrame:
        '''pass element and return text'''
        # attributes = self.attributes(element)
        # try:
        #     values = attributes[name].values
        # except:
        #     values = False
        # return values
        #columns = self.root.find(xpath, self.namespaces)
        #if columns is not None:
        for i in self.root.findall(xpath, self.namespaces):
            try:
                #text = i.find('Question').text
                #OID = i.get('OID')
                #print(OID)
                #print(i.find('Question/TranslatedText'))
                #print("".join(i.itertext()))
                #return text
                print(i.tag, i.text)
                #rint(text)
            except:
                pass
            #return pd.DataFrame(
            #    [i.text for i in self.root.findall(xpath, self.namespaces)], columns=list(columns.attrib))
        #return None