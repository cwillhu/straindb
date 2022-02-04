
set global local_infile=1;

-- Note: Replace '/Path/to/output_directory' below with your output_directory location (specified in config.yaml)

-- Load filtered plasmid table into staging table (Note 'filter' subdirectory below)
load data local infile '/Path/to/output_directory/out/filter/plasmid.csv'
  into table staging_plasmid
  fields terminated by ','
  optionally enclosed by '"'
  escaped by '"'
  lines terminated by '\r\n'
  ignore 1 lines
  (plasmid_original_line_number, name, expanded_name, source, parent1, parent2,
    restriction_site, datestr);

-- Load filtered and normalized allele table into staging table (Note 'normalize' subdirectory below)
load data local infile '/Path/to/output_directory/normalize/allele.csv'
  into table staging_allele
  fields terminated by ','
  optionally enclosed by '"'
  escaped by '"'
  lines terminated by '\r\n'  
  ignore 1 lines
  (allele_original_line_number, name, allele_type, gene_name, plasmid_name, comment);

-- Load filtered and normalized strain_allele table. (Note 'normalize' subdirectory below)
load data local infile '/Path/to/output_directory/out/normalize/strain_allele.csv'
  into table staging_strain_allele
  fields terminated by ','
  optionally enclosed by '"'
  escaped by '"'
  lines terminated by '\r\n'  
  ignore 1 lines
  (strain_original_line_number, strain_name, chromosome, alleleset_binaryid, allele_name, gene_name,
    heterozygous, other_names, source, comment);

-- Load table of distinct strain names
insert into staging_strain (strain_name) select distinct strain_name from staging_strain_allele;
