import xml.etree.ElementTree as ET
import re
import pandas as pd

class Redcap:
    """Read and parse REDCap CDISC ODM"""

    def __init__(self, file):
        """Read and extract (meta)data from REDCap CDISC ODM
        
        pass valid xml file path"""
        self.file = file
        
        self.readParseXML(file)
        self.namespace()
        
        self.namespaces = {'odm': self.namespace}
         
    def readParseXML(self, file):
        """Read and parse xml"""
        try:
            tree = ET.parse(file)
            self.root = tree.getroot()
        except FileNotFoundError:
            print('File not found, please give correct file path.')
            exit
        except ET.ParseError:
            print('ParseError, please provide valid xml file.')
            exit

    def namespace(self):
        """Return the namespace uri for the current file"""
        root = self.root
        try:
            c = re.compile(r'\{(.+)\}')
            m = c.match(root.tag)
            self.namespace = m.group(1)
        except:
            print('Failed to retrieve namespace.')
            exit
    
    def attributes(self, xpath):
        """Returns Pandas DataFrame of found attributes"""
        root = self.root
        columns = root.find(xpath, self.namespaces)
        if columns == None:
            # if xpath resulted with no result return None
            return None
        else:
            df = pd.DataFrame([],columns=list(columns.attrib))
            for i in root.findall(xpath, self.namespaces):
                df = df.append(i.attrib, ignore_index=True)
            return df

    def attribute(self, xpath):
        """Returns Pandas DataFrame of found attribute"""
        root = self.root
        columns = root.find(xpath, self.namespaces)
        if columns == None:
            # if xpath resulted with no result return None
            return None
        else:
            df = pd.DataFrame([],columns=list(columns.attrib))
            i = root.find(xpath, self.namespaces)
            df = df.append(i.attrib, ignore_index=True)
            return df

    def iterfind(self, xpath):
        """Return tree"""
        root = self.root
        return root.iterfind(xpath, self.namespaces)

    # def findall(self, xpath):
    #     """Search tree for specific argument value and return ET"""
    #     root = self.root
    #     #for i in root.findall(xpath, self.namespaces):
    #     #    print(i)
    #     return root.findall(xpath, self.namespaces)

    # def tagText(self, xpath):
    #     """Return tag text as str"""
    #     root = self.root
    #     i = root.find(xpath, self.namespaces)
    #     return i.text

    