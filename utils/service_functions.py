
################################################
'''
Antwerp		2000-2999
Brussels	1000-1299
East Flanders		9000-9999
Flemish Brabant		1500-1999, 3000-3499
Hainaut			6000-6599, 7000-7999
Liege		4000-4999
Limburg		3500-3999
Luxembourg		6600-6900
Namur		5000-5999
Walloon Brabant		1300-1499
West Flanders	8000-8999
'''

def get_province_by_postcode(pcode: int):
    """
    Convert belgium postal code to the name of province (and abstract number)
    """
       
    if 1000 <= pcode <= 1299:
        return 10, 'Brussels'
    elif 1300 <= pcode <= 1499:
        return 1,'Walloon Brabant'
    elif 1500 <= pcode <= 1999 or 3000 <= pcode <= 3499:
        return 3, 'Flemish Brabant'
    elif 2000 <= pcode <= 2999:
        return 2, 'Antwerp'
    elif 3500 <= pcode <= 3999:
        return 9, 'Limburg'
    elif 4000 <= pcode <= 4999:
        return 4, 'Liege'
    elif 5000 <= pcode <= 5999:
        return 5, 'Namur'
    elif 6000 <= pcode <= 6599 or 7000 <= pcode <= 7999:
        return 7, 'Hainaut'
    elif 6600 <= pcode <= 6999:
        return 6, 'Luxembourg'
    elif 8000 <= pcode <= 8999:
        return 8, 'West Flanders'
    elif 9000 <= pcode <= 9999:
        return 9, 'East Flanders'
    else:
        print('Incorrect code:',pcode)
        return 0,'Incorrect postal code'

#############################################

def get_region_by_postcode(pcode: int):
    """
    Convert belgium postal code to the name of region (and abstract number)
    """
    if 1000 <= pcode <= 1299:
        return 1, 'Brussels'
        
    elif 1300 <= pcode <= 1499 or 4000 <= pcode <= 7999:
        return 2,'Wallonia'
        
    elif 1500 <= pcode <= 3999 or 8000 <= pcode <= 9999:
        return 3, 'Flanders'
    else:
        print('Incorrect code:',pcode)
        return 0,'Incorrect postal code'



