from src import Transform

class main:
    """Transform REDCap CDISC ODM to Molgenis EMX2"""

    # example 1 (meta data only)
    #Transform('data/Example_1_REDCap_meta.xml')
    
    # example 2 (meta and data), not fully compatible with EMX2 (upload to Molgenis fails if repeated measures are used)
    Transform('data/Example_2_REDCap_repeated-measures.xml')
    
    # example 3 (meta data only)
    #Transform('data/Example_3_TestHumanCancer_REDCap.xml')

    # example 4 (meta and data)
    #Transform('data/Example_4_TestHumanCancer_data_REDCap.xml')

if __name__ == "__main__":
    main()