from src.molgenis.transform import Transform

class main:
    """Transform REDCap CDISC ODM to Molgenis EMX2"""

    # example 1 (meta data and data)
    #Transform(file = 'data/Example_1_REDCap_meta.xml', edc = 'REDCap')
    
    # example 2 (meta data and data), not fully compatible with EMX2 (upload to Molgenis fails if repeated measures are used)
    Transform('data/Example_2_REDCap_repeated-measures.xml', 'REDCap')
    
    # example 3 (meta data and data)
    #Transform('data/Example_3_TestHumanCancer_REDCap.xml', 'REDCap')

    # example 4 (meta data and data)
    #Transform('data/Example_4_TestHumanCancer_data_REDCap.xml', 'REDCap')

    # example 5 (missing clinical data)
    #Transform('data/Example_5_missing-clinical-data.xml', 'REDCap')

    # example 6 (not a xml file)
    #Transform('data/Example_6_not-a-xml-file.docx', 'REDCap')

if __name__ == "__main__":
    main()