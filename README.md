# Transform REDCap CDISC ODM to EMX2

## Usage

`python run.py`

Execute the script which will transform the example xml (REDCap CDISC ODM) to EMX2 format.

### Example files

Four example are included and can be found in the `data` directory:

- Example_1_REDCap_meta.xml
- Example_2_REDCap_repeated-measures.xml
- Example_3_TestHumanCancer_REDCap.xml
- Example_4_TestHumanCancer_data_REDCap.xml
- Example_5_missing-clinical-data.xml
- Example_6_not-a-xml-file.docx

### Output files

After running the script you will find the output in `data/output/`

Minimum output should be a *molgenis.csv*, *SubjectData.csv* and *\<instrument\>.csv*.

### Upload to MOLGENIS EMX2

Examples without repeated measures (or any data) should load into MOLGENIS (Example file 1,3 and 4). Repeated measures (Example file 2) are transformed to EMX2 but **not** compatible yet, import into MOLGENIS will fail. Example 5 and 6 should fail.

### Issues

- ~~data export from REDCap without repeated measures fails~~
- ~~EMX Key issue~~
- ~~Collapse REDCap multiple choice to EMX TEXT~~
- ~~Add ref table to molgenis.csv, SubjectData.csv~~
- zip output data and option to remove (cleanup) output folder
- Transform CodeList to Variables and VariableValues

## UMCG REDCap

If you want to try and transform your own data please follow the steps below to download the data.

1. Got to [https://redcap.umcg.nl/](https://redcap.umcg.nl/) and login.
2. Select the project you want to export the data from (meta and data).
3. Select the tab 'Other Functionality' and there under 'Copy or Back Up the Project' click on 'Download metadata & data (xml)'.
4. A popup window will appear and select the option 'Include all uploaded files and signatures' (if applicable) , then click on 'Export Entire Project (metadata & data)'.
