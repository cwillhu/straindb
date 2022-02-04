''' Clean allele string (remove suffix), determine allele type, return error type, if any '''

import re

DEBUG = False

def parse_allele(allele_name):

    if DEBUG: print('\nAllele: ' + allele_name)

    allele_type = 'other'
    err_key = None

    if allele_name == '' or not re.match(r'^([a-zA-Z]+[0-9]+[a-z]*)+$', allele_name):

        err_key = 'invalid_allele_name'
        return (None, None, err_key)

    # Remove any non-numeric suffix characters
    allele_name = re.sub(r'[a-z]+$','',allele_name)

    # Determine allele type
    if re.match(r'^([a-z]{1,3}[0-9]+)+$', allele_name):

        allele_type = 'mutant'
        
    elif re.match(r'^[a-z]{1,3}(Ex|Is|Si)[0-9]+$', allele_name):

        allele_type = 'transgene'

    elif re.match(r'^[a-z]{1,3}(T|C|In|Df)[0-9]+$', allele_name):

         allele_type = 'rearrangement'

    else:
        
        allele_type = 'other'

    if DEBUG: print(f'allele_type: {allele_type}')

    return (allele_name, allele_type, err_key)
    
