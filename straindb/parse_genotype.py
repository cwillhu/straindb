''' Parse genotype string (e.g., "tm290/e189 III; nsIs53 IV; kyIs136 X") '''

from copy import deepcopy
import re
import json

DEBUG = False
TEST = False

genotype_item = {'chromosome': None,
                 'allelesets': {}
                 }

def gprint(genotype):
    print('Parsed:\n' + json.dumps(genotype, indent=4) + '\n')

def parse_genotype(genotype_str):

    genotype = []

    genotype_str = genotype_str.strip()

    if DEBUG: print('\nGenotype String: ' + genotype_str)

    # Remove bracketed substrings (may contain plasmid name, plasmid expanded name, etc)
    genotype_str = re.sub(r'\[.*?\]', '', genotype_str)

    # Remove substrings denoting line number
    genotype_str = re.sub(r'\(line [0-9]+\)', '', genotype_str)

    # Split genotype string into subunits
    genotype_item_strs = re.split(r'\s*;\s*', genotype_str)

    # Iterate over genotype subunits
    for item_str in genotype_item_strs:

        if DEBUG: print('  Item: ' + item_str)

        item = deepcopy(genotype_item)

        # capture chromosome name, if present
        if m := re.match(r'^(?P<nonchr>[-+.)(a-zA-Z0-9\s/]+?)\s*(?P<chr>I|II|III|IV|V|X)?$', item_str):
            chr = item_str[m.start('chr'):m.end('chr')]
            nonchr = item_str[m.start('nonchr'):m.end('nonchr')]
            if DEBUG: print(f'    chr: __{chr}__')            
            if DEBUG: print(f'    nonchr: __{nonchr}__')

            if chr:
                item['chromosome'] = chr

            asets_list = re.split(r'\s*/\s*', nonchr) # seperate allele sets, if needed

            heterozygous = False
            if len(asets_list) == 2:
                heterozygous = True
                if '+' in asets_list: asets_list.remove('+')  # do not track wild type allele

            for i in range(0,len(asets_list)):  # asets_list is length 1 or 2
                aset_str = asets_list[i]
                item['allelesets']['alleleset' + str(i+1)] = []

                # list of alleles, each potentially with a gene name
                regex = re.compile(r'(?P<gene>[-.a-zA-Z0-9]+)\s*\((?P<allele_of_gene>[-a-zA-Z0-9]+)\)|(?P<allele>[-a-zA-Z0-9]+)')
                for m in regex.finditer(aset_str):
                    allele_dict = {}
                   
                    match_dict = m.groupdict()
                    if match_dict['allele']:
                        allele_dict['allele_name'] = match_dict['allele']
                    elif match_dict['allele_of_gene']:
                        allele_dict['allele_name'] = match_dict['allele_of_gene']
                        allele_dict['gene_name'] = match_dict['gene']                        
                        
                    if allele_dict:
                        allele_dict['heterozygous'] = heterozygous
                        item['allelesets']['alleleset' + str(i+1)].append(allele_dict)

            genotype.append(item)
            
        else:  #genotype item could not be parsed
            if DEBUG: print('Genotype could not be parsed')
            return None #failure return value
            
    if DEBUG: gprint(genotype)

    return genotype  #dict


if TEST:    
    gens = [
        'e123/dec-2(e200) e321 X',
        'ced-3 (n717) IV; ok700/nT1 (qIs51); bec-1',
        'ced-3 (n717) IV; ok700/ok701 e23 gen-10 (e1234) II; bec-1'
    ]

    for gen in gens:
        parse_genotype(gen)

