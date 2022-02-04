

drop table if exists staging_strain;
create table staging_strain (
    id int primary key auto_increment,
    strain_name varchar(100) not null,
    processed int default 0
);

drop table if exists staging_strain_allele;
create table staging_strain_allele (
    id int primary key auto_increment,
    strain_original_line_number int,
    strain_name varchar(100) not null,
    chromosome varchar(10),
    alleleset_binaryid int,
    allele_name varchar(100),
    gene_name varchar(100),
    heterozygous boolean,
    other_names varchar(100), 
    source varchar(100), 
    comment text,
    processed int default 0    
);

drop table if exists staging_allele;
create table staging_allele (
    id int primary key auto_increment,
    allele_original_line_number int,
    name varchar(100) not null,
    allele_type enum('mutant', 'transgene', 'rearrangement', 'other'),
    gene_name varchar(100),
    plasmid_name varchar(100),
    comment text,
    processed int default 0        
);


drop table if exists staging_plasmid;
create table staging_plasmid (
    id int primary key auto_increment,
    plasmid_original_line_number int,
    name varchar(100) not null,
    expanded_name varchar(200) not null,
    source varchar(100),
    parent1 varchar(100),
    parent2 varchar(100),
    restriction_site varchar(100),
    datestr varchar(50)
);


