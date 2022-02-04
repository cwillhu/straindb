''' Select rows and columns of strain, allele and plasmid CSV files, without altering table structure '''

import csv, re
from pathlib import Path
from collections import OrderedDict
from copy import copy
import datetime, dateutil
from dateutil.parser import parse
from straindb.config import rawCSV, output_directory
from straindb.parse_genotype import parse_genotype
from straindb.fileio import get_reader, get_writer, read_header, write_header, mkparent
from straindb.parse_allele import parse_allele

DEBUG = False

outdir = output_directory / 'filter'
errdir = output_directory / 'filter_errorlog'
errstats_file = errdir / 'errstats.txt'

        
def err_item(fileroot, err_name):  #err_item is container for error file attributes
    basename = fileroot + '.' + err_name + '.csv'  # name of error file
    return (
        OrderedDict(
            [('file', errdir / basename),
             ('err_count', 0),
             ('writer', None)])
    )


def write_failure(err_item, row):
    # Increment error count for this err_item
    err_item['err_count'] += 1

    # Write failing row to error file
    err_item['writer'].writerow(row)


def write_errfile_headers(raw_header, err):  #write a header line to all error files
    err_header = copy(raw_header)
    err_header.insert(0,'Original Line Number')
    for err_item in err.values():
        errfile = err_item['file']
        mkparent(errfile)
        write_header(errfile, err_header)

        
def initialize_errorlog(): # create errstats.txt and write initial log information
    mkparent(errstats_file)
    with open(errstats_file, 'w') as f:
        f.write('Script: \n  ' + __file__ + '\n\n')
        f.write('Input files: \n  ' + '\n  '.join([str(x) for x in rawCSV.values()]) + '\n\n')
        f.write('Output files: \n  ' + '\n  '.join(f'{outdir / x}.csv' for x in ['strain','allele','plasmid']) + '\n\n')
        f.write('Error log directory: \n  ' + str(errdir) + '\n\n')
        f.write('ERROR STATISTICS\n----------------\n')        


def write_plasmids():  # Write valid plasmids to plasmid.csv and invalid plasmids to error files

    raw_header = read_header(rawCSV['plasmid'])
    
    # Define error files
    err = OrderedDict()
    err['duplicate_plasmid']     = err_item('plasmid', 'duplicate_plasmid')    
    err['invalid_plasmid_name']  = err_item('plasmid', 'invalid_plasmid_name')
    err['invalid_expanded_name'] = err_item('plasmid', 'invalid_expanded_name')
    err['invalid_date']          = err_item('plasmid', 'invalid_date')    
    
    # Define and initialize plasmid table file
    plasmid_outfile = outdir / 'plasmid.csv'
    plasmid_header = ['plasmid_original_line_number', 'name', 'expanded_name', 'source', 'parent1', 'parent2', 'restriction_site', 'date']
    write_header(plasmid_outfile, plasmid_header)    

    # Initialize error files by writing header line to each file
    write_errfile_headers(raw_header, err)    

    #open all output files
    with open(err['duplicate_plasmid']['file'], 'a')     as duplicate_plasmid_fout, \
         open(err['invalid_plasmid_name']['file'], 'a')  as invalid_plasmid_name_fout, \
         open(err['invalid_expanded_name']['file'], 'a') as invalid_expanded_name_fout, \
         open(err['invalid_date']['file'], 'a')          as invalid_date_fout, \
         open(rawCSV['plasmid'], 'r')                    as plasmid_raw_fin, \
         open(plasmid_outfile, 'a')                      as plasmid_fout:

        err['duplicate_plasmid']['writer']     = get_writer(duplicate_plasmid_fout)         
        err['invalid_plasmid_name']['writer']  = get_writer(invalid_plasmid_name_fout)
        err['invalid_expanded_name']['writer'] = get_writer(invalid_expanded_name_fout)
        err['invalid_date']['writer']          = get_writer(invalid_date_fout)        

        plasmid_raw   = get_reader(plasmid_raw_fin)
        plasmid       = get_writer(plasmid_fout)

        # Write valid rows to outfile and invalid rows to error log files        
        num_successes = 0
        next(plasmid_raw) # skip header line
        linenum = 1
        plasmid_names = []
        for r in plasmid_raw: 
            linenum += 1
            r = [x.strip() for x in r]

            expanded_name    = r[2]
            plasmid_name     = r[5]
            date             = r[6]
            parent1          = r[7]
            parent2          = r[8]
            restriction_site = r[9]
            source           = r[13]

            # Check error conditions
            failure = False
            if plasmid_name == '' or not re.match(r'p[a-zA-Z]+[0-9]+', plasmid_name):

                write_failure(err['invalid_plasmid_name'], [linenum] + r)
                failure = True

            elif plasmid_name in plasmid_names:

                write_failure(err['duplicate_plasmid'], [linenum] + r)
                failure = True

            else:

                plasmid_names.append(plasmid_name)
                
            if date == '':  # allow date to be empty

                date = 'NULL'

            else: # validate date 
                try:
                    dt = parse(date, fuzzy=True)
                except dateutil.parser._parser.ParserError:
                    write_failure(err['invalid_date'], [linenum] + r)                    
                date = f'{dt.year}-{dt.month}-{dt.day}'
                
            if expanded_name == '':

                write_failure(err['invalid_expanded_name'], [linenum] + r)
                failure = True

            if not failure: # success! write clean plasmid table row to output file
                if parent1 == '': parent1 = 'NULL';
                if parent2 == '': parent2 = 'NULL';
                if restriction_site == '': restriction_site = 'NULL';
                if source == '': source = 'NULL';                
                plasmid.writerow([linenum, plasmid_name, expanded_name, source, parent1, parent2, restriction_site, date])
                num_successes += 1
                
            if DEBUG and linenum > 250: break

    num_raw_plasmids = linenum - 1 # subtract 1 for header line
    errstats = []
    errstats += [f'\nPLASMIDS:']
    errstats += [f'  Rows processed: {num_raw_plasmids}']
    errstats += [f'  Valid rows: {num_successes}']
    errstats += [f"    Invalid plasmid_name: {err['invalid_plasmid_name']['err_count']}"]
    errstats += [f"    Invalid expanded_name: {err['invalid_expanded_name']['err_count']}"]
    errstats += [f'  Success Rate: {int(100*num_successes/num_raw_plasmids)}%']
    
    print('\n'.join(errstats))
          
    #write statistics to error log
    with open(errstats_file, 'a') as f:
        f.write('\n'.join(errstats) + '\n')

        
def write_alleles():  # Write valid alleles to allele.csv and invalid alleles to error files

    raw_header = read_header(rawCSV['allele'])
    
    # Define error files
    err = OrderedDict()
    err['duplicate_allele']    = err_item('allele', 'duplicate_allele')    
    err['invalid_allele_name'] = err_item('allele', 'invalid_allele_name')
    
    # Initialize error files by writing header line
    write_errfile_headers(raw_header, err)        

    # Define and initialize allele table file
    allele_outfile = outdir / 'allele.csv'
    allele_header = ['allele_original_line_number', 'allele_name', 'allele_type', 'gene_name', 'plasmids', 'comment']
    write_header(allele_outfile, allele_header)

    #open all output files    
    with open(err['duplicate_allele']['file'], 'a')     as duplicate_allele_fout, \
         open(err['invalid_allele_name']['file'], 'a')  as invalid_allele_name_fout, \
         open(rawCSV['allele'], 'r')                    as allele_raw_fin, \
         open(allele_outfile, 'a')                      as allele_fout:

        err['invalid_allele_name']['writer'] = get_writer(invalid_allele_name_fout)
        err['duplicate_allele']['writer']    = get_writer(duplicate_allele_fout)        

        allele_raw   = get_reader(allele_raw_fin)
        allele = get_writer(allele_fout)

        # Write valid rows to outfile and invalid rows to error log files        
        num_successes = 0
        next(allele_raw) # skip header line
        linenum = 1
        allele_names = []
        for r in allele_raw:
            linenum += 1
            r = [x.strip() for x in r]

            allele_name = r[2]
            gene_name   = r[3]
            comment     = r[5]
            plasmids    = r[8]

            # Parse allele_name
            (allele_name, allele_type, allele_err_key) = parse_allele(allele_name)

            # Check error conditions
            failure = False
            if allele_err_key:

                write_failure(err[allele_err_key], [linenum] + r)
                failure = True
            
            elif allele_name in allele_names:

                write_failure(err['duplicate_allele'], [linenum] + r)
                failure = True
                
            else:

                allele_names.append(allele_name)

            if not failure: # success! write clean allele data to output file

                if gene_name == '': gene_name = 'NULL'

                comment = 'NULL' if comment == '' else re.sub(r'\n', ' ', comment) 
                
                allele.writerow([linenum, allele_name, allele_type, gene_name, plasmids, comment])
                num_successes += 1
                
            if DEBUG and linenum > 250: break

    num_raw_alleles = linenum - 1 # subtract 1 for header line
    errstats = []
    errstats += [f'\nALLELES:']
    errstats += [f'  Rows processed: {num_raw_alleles}']
    errstats += [f'  Valid rows: {num_successes}']
    errstats += [f"    Invalid allele_name: {err['invalid_allele_name']['err_count']}"]
    errstats += [f'  Success Rate: {int(100*num_successes/num_raw_alleles)}%']
    
    print('\n'.join(errstats))
          
    #write statistics to error log
    with open(errstats_file, 'a') as f:
        f.write('\n'.join(errstats) + '\n')

        
def write_strains():  # Write valid strains to strain.csv and invalid strains to error files

    raw_header = read_header(rawCSV['strain'])
    
    # Define error files
    err = OrderedDict()
    err['duplicate_strain']    = err_item('strain', 'duplicate_strain')    
    err['invalid_strain_name'] = err_item('strain', 'invalid_strain_name')
    err['invalid_genotype']    = err_item('strain', 'invalid_genotype')
    
    # Initialize error files by writing header line
    write_errfile_headers(raw_header, err)        

    # Define and initialize strain table file
    strain_outfile = outdir / 'strain.csv'
    strain_header = ['strain_original_line_number', 'strain_name', 'genotype', 'source', 'other_names', 'comment']
    write_header(strain_outfile, strain_header)
  
    with open(err['duplicate_strain']['file'], 'a')    as duplicate_strain_fout, \
         open(err['invalid_strain_name']['file'], 'a') as invalid_strain_name_fout, \
         open(err['invalid_genotype']['file'], 'a')    as invalid_genotype_fout, \
         open(rawCSV['strain'], 'r')                   as strain_raw_fin, \
         open(strain_outfile, 'a')                     as strain_fout:

        err['duplicate_strain']['writer']    = get_writer(duplicate_strain_fout)
        err['invalid_strain_name']['writer'] = get_writer(invalid_strain_name_fout)        
        err['invalid_genotype']['writer']    = get_writer(invalid_genotype_fout)

        strain_raw = get_reader(strain_raw_fin)
        strain     = get_writer(strain_fout)

        # Write valid rows to outfile and invalid rows to error log files
        num_successes = 0
        next(strain_raw) # skip header line
        linenum = 1
        strain_names = []
        for r in strain_raw: 
            linenum += 1
            r = [x.strip() for x in r]

            strain_name = r[2]
            genotype    = r[8]
            source      = r[9]
            comment     = r[11]
            other_names = r[15]

            if genotype.upper == 'WT': genotype = ''
            
            # Check error conditions
            failure = False
            if strain_name == '' or not re.match(r'CHB[0-9]+', strain_name):

                write_failure(err['invalid_strain_name'], [linenum] + r)
                failure = True

            elif strain_name in strain_names:

                write_failure(err['duplicate_strain'], [linenum] + r)
                failure = True                

            else:

                strain_names.append(strain_name)
                
            if genotype != '':  #allow empty genotype string

                if not re.match(r'^[-+.\]\[)(a-zA-Z0-9\s/;]+$', genotype):

                    write_failure(err['invalid_genotype'], [linenum] + r)
                    failure = True

                else:
                    genotype_dict = parse_genotype(genotype)

                    if genotype_dict is None:
                        if DEBUG: print(f'Could not parse genotype: {genotype}')
                        failure = True
                    else:
                        genotype = str(genotype_dict)

            if not failure: # success! write clean strain data to output file

                if other_names == '': other_names = 'NULL'

                if genotype == '': genotype = 'NULL'

                if source == '': source = 'NULL'

                comment = 'NULL' if comment == '' else re.sub(r'\n', ' ', comment) 

                strain.writerow([linenum, strain_name, genotype, source, other_names, comment])
                num_successes += 1
                
            if DEBUG and linenum > 250: break

    num_raw_strains = linenum - 1  # subtract 1 for header line
    errstats = []
    errstats += [f'\nSTRAINS:']
    errstats += [f'  Rows processed: {num_raw_strains}']
    errstats += [f'  Valid rows: {num_successes}']
    errstats += [f"    Invalid strain_name: {err['invalid_strain_name']['err_count']}"]
    errstats += [f"    Invalid genotype: {err['invalid_genotype']['err_count']}"]
    errstats += [f'  Success Rate: {int(100*num_successes/num_raw_strains)}%']
    
    print('\n'.join(errstats))
          
    #write statistics to error log
    with open(errstats_file, 'a') as f:
        f.write('\n'.join(errstats) + '\n')

        
initialize_errorlog()
write_strains()    
write_alleles()
write_plasmids()
