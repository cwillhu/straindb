
-- Summary of data loaded into DB

-- Staging tables:
select count(*) from staging_strain;

select count(*) from staging_strain_allele;
select count(distinct strain_name) from staging_strain_allele;
select count(distinct allele_name) from staging_strain_allele;

select count(*) from staging_allele;
select count(distinct name) from staging_allele;

select count(*) from staging_plasmid;

-- Error tables:
select count(*) from allele_missing_from_staging_allele_table;
select count(distinct strain_name) from allele_missing_from_staging_allele_table;

select count(*) from plasmid_missing_from_staging_plasmid_table;
select count(distinct strain_name) from allele_missing_from_staging_allele_table;

select count(*) from allele_no_allele_type;

-- Strain, allele and plasmid tables:
select count(*) from strain;
select count(*) from allele;
select count(*) from plasmid;
