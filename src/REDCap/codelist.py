'''Get data from REDCap CDISC ODM and convert to codelist if available for instrument'''

# <MetaDataVersion ...>

    # <ItemDef OID="mc_drop_single_1" Name="mc_drop_single_1" DataType="text" Length="1" redcap:Variable="mc_drop_single_1" redcap:FieldType="select" redcap:FieldNote="Select your favorite" redcap:SectionHeader="&lt;div class=&quot;rich-text-field-label&quot;&gt;&lt;h2&gt;Multiple choice&lt;/h2&gt;&lt;/div&gt;">
	# 	<Question><TranslatedText>Multiple Choice Drop Down list (single answer)</TranslatedText></Question>
	# 	<CodeListRef CodeListOID="mc_drop_single_1.choices"/>
	# </ItemDef>

#     <CodeList OID="mc_drop_single_1.choices" Name="mc_drop_single_1" DataType="text" redcap:Variable="mc_drop_single_1">
# 		<CodeListItem CodedValue="1"><Decode><TranslatedText>Apple</TranslatedText></Decode></CodeListItem>
# 		<CodeListItem CodedValue="2"><Decode><TranslatedText>Pear</TranslatedText></Decode></CodeListItem>
# 		<CodeListItem CodedValue="3"><Decode><TranslatedText>Windows ME</TranslatedText></Decode></CodeListItem>
# 		<CodeListItem CodedValue="4"><Decode><TranslatedText>Warm socks</TranslatedText></Decode></CodeListItem>
# 	</CodeList>

#{instrument}_{codelist}_{OID}
# 1, Apple
# 2, Pear
# 3, Windows ME
# 4, Warm socks

#{instrument}_{codelist}
# {OID}, 1, Apple
# {OID}, 2, Pear
# {OID}, 3, Windows ME
# {OID}, 4, Warm socks

# VariableValues
# release, variable, value, label, order, isMissing, ontologyTermIRI
# 1.0.0, mc_drop_single_1, 1, Apple, 1, ,,
# 1.0.0, mc_drop_single_1, 2, Pear, 2, ,,
# 1.0.0, mc_drop_single_1, 3, Windows ME, 3, ,,
# 1.0.0, mc_drop_single_1, 4, Warm socks, 4, ,,

# Variables
# release, table, name, collectionEvent, mappings, label, format, unit, references, mandatory, description, order, exampleValues, permittedValues, keywords, repeats, vocabularies, notes,
# release, table, name, label
# 1.0.0, Form, record_id, <question><translatedtext> ..

# Releases
# resource, version, tables, models, databanks, cohorts, date, description

# Resources
# pid, name, localName, acronym, website, description, keywords, contributors, externalIdentifiers, institution, logo, numberOfParticipants, numberOfParticipanstWithSamples, countries, regions, ..
import configparser
import pandas as pd

import src.cdisc
#from cdisc import Cdisc

class REDCapCodelist:
	config = configparser.ConfigParser()
	config.read('./src/config.ini')

	ns = config['redcap']['namespace']
	output_folder = config['settings']['output_folder']

	def __init__(self, file: str) -> None:
		self.file = file
	
	def codelist_data_table(self) -> None:
		'''retrieve codelist (molgenis variables) data'''
		xml = src.cdisc.Cdisc(self.file, 'REDCap')

		def get_forms(self) -> pd.DataFrame:
			'''Returns a pandas DataFrame with to columns: OID, FormName'''
			# determine which forms are included and need to be extracted
			return pd.concat([
				pd.Series(src.cdisc.Cdisc.attribute_values(xml, './/odm:FormDef', 'OID'), name='OID'), 
				pd.Series(src.cdisc.Cdisc.attribute_values(xml, './/odm:FormDef', self.ns + 'FormName'), name='FormName')], axis=1)
		
		#print(get_forms(self))

		def get_item_group_def(self) -> pd.DataFrame:
			'''Returns a pandas DataFrame with to columns: OID, FormName'''
			# determine which forms are included and need to be extracted
			return pd.Series(src.cdisc.Cdisc.attribute_values(xml, './/odm:ItemGroupDef', 'OID'), name='OID')
		
		#print(get_item_group_def(self))

		def get_item_def(self) -> pd.DataFrame:
			'''Returns a pandas DataFrame with to columns: OID, FormName'''
			# determine which forms are included and need to be extracted
			return pd.concat([
				#pd.Series(Cdisc.attribute_values(xml, './/odm:ItemDef', 'OID'), name='OID'),
				#pd.Series(Cdisc.element_text(xml, './/odm:ItemDef'), name='text')])
				pd.Series(src.cdisc.Cdisc.element_text(xml, './/odm:ItemDef/odm:Question/odm:TranslatedText'), name='text')])

		print(get_item_def(self))