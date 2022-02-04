''' Normalize strain table (remove genotype dict) and allele table (remove plasmid list) '''

import csv, re, ast
from pathlib import Path
from collections import OrderedDict
from straindb.config import rawCSV, output_directory
from straindb.fileio import get_writer, get_reader, mkparent

DEBUG = False
debug_line_number = None # set DEBUG to True and debug_line_number to a line number in original strain CSV to debug

indir = output_directory / 'filter'
outdir = output_directory / 'normalize'

strain_file = indir / 'strain.csv'
allele_file = indir / 'allele.csv'

strain_allele_outfile = outdir / 'strain_allele.csv'
strain_allele_outfile_header = ['strain_original_line_number', 'strain_name', 'chromosome',
                                'alleleset_binaryid', #alleleset_binaryid is either 1 or 2
                                'allele_name', 'gene_name', 'heterozygous',
                                'source', 'other_name', 'comment']  

allele_outfile = outdir / 'allele.csv'
allele_outfile_header = ['allele_original_line_number', 'allele_name', 'allele_type', 'gene_name', 'plasmid_name', 'comment']

def normalize_strain(): # Normalize strain table (i.e., flatten genotype dict)

    mkparent(strain_allele_outfile)
    with open(strain_file, 'r') as strain_fin, \
         open(strain_allele_outfile, 'w') as strain_allele_fout:
         
        strain_reader        = get_reader(strain_fin)
        strain_allele_writer = get_writer(strain_allele_fout)

        strain_allele_writer.writerow(strain_allele_outfile_header)

        if DEBUG: print(strain_allele_outfile_header)
        
        next(strain_reader) #skip header line
        rows_processed = 0
        for r in strain_reader:
            rows_processed += 1
            r = [x.strip() for x in r] 

            strain_original_line_number = r[0]
            strain_name = r[1]
            genotype = ast.literal_eval(r[2]) if r[2] != 'NULL' else None
            source = r[3]
            other_names = r[4]
            comment = r[5]

            if DEBUG and strain_original_line_number != str(debug_line_number): continue

            if DEBUG: print('strain_original_line_number: ' + strain_original_line_number)
            if DEBUG: print('genotype: ' + str(genotype))

            if genotype is None:
                tablerow = [strain_original_line_number, strain_name] + 5*['NULL'] + [source, other_names, comment]
                strain_allele_writer.writerow(tablerow)
                continue

            #write one row in strain_allele file for each allele in each alleleset in genotype
            for g in genotype:

                allelesets_list = list(g['allelesets'].values())
                chromosome = g['chromosome'] if g['chromosome'] else 'NULL'

                #make first pass to retrieve alleleset membership in order to verify heterzygosity in second pass
                nameslist = [[], []]
                for i in range(0,len(allelesets_list)):
                    aset = allelesets_list[i]
                    for allele in aset:
                        nameslist[i].append(allele['allele_name'])

                #iterate over allelesets, writing rows to CSV file
                for i in range(0,len(allelesets_list)):
                    aset = allelesets_list[i]
                    aset_binaryid = i + 1
                    for allele in aset:
                        allele_name = allele['allele_name']
                        gene_name = allele['gene_name'] if 'gene_name' in allele.keys() else 'NULL'
                        heterozygous = int(allele['heterozygous']) # cast to int for MySQL tinyint "boolean"

                        # verify heterozygosity by checking if allele name appears in opposing allele set
                        if i == 0: 
                            if allele_name in nameslist[1]: heterozygous = int(False)
                        elif i == 1:
                            if allele_name in nameslist[0]: heterozygous = int(False)
                            
                        tablerow = [strain_original_line_number, strain_name, chromosome,
                                    aset_binaryid, allele_name, gene_name, heterozygous,
                                    other_names, source, comment]
                        
                        if DEBUG: print(tablerow)
                        strain_allele_writer.writerow(tablerow)


def normalize_allele(): #Normalize allele table (split plasmid list into separate rows in table)

    mkparent(allele_outfile)
    with open(allele_file, 'r') as allele_fobj, \
         open(allele_outfile, 'w') as allele_outfile_fobj:

        allele_reader = get_reader(allele_fobj)
        allele_writer  = get_writer(allele_outfile_fobj)

        allele_writer.writerow(allele_outfile_header)
        if DEBUG: print(allele_outfile_header)
        
        next(allele_reader) #skip header line
        rows_processed = 0
        for r in allele_reader:
            rows_processed += 1
            r = [x.strip() if x != '' or None else 'NULL' for x in r] 

            allele_original_line_number = r[0]
            allele_name = r[1]
            allele_type = r[2]            
            gene_name = r[3]
            plasmids = r[4]     
            comment = r[5]

            if DEBUG and allele_original_line_number != str(debug_line_number): continue

            #split plasmid list
            plasmid_list = re.split(r'\s*[,;]\s*', plasmids)
            for plasmid in plasmid_list:
                allele_writer.writerow([allele_original_line_number, allele_name, allele_type, gene_name, plasmid, comment])

            
normalize_strain();
normalize_allele();
