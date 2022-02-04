    
drop table if exists strain;
create table strain (
    id int primary key auto_increment, 
    name varchar(100) not null, 
    other_names varchar(100) default null, 
    source varchar(100), 
    comment text default null
);

drop table if exists gene;
create table gene (
    id int primary key auto_increment,
    name varchar(20) not null
);

drop table if exists allele;
create table allele (
    id int primary key auto_increment, 
    name varchar(100) not null,
    allele_type enum('mutant', 'transgene', 'rearrangement', 'other'),
    gene_id int default null,
    comment text default null
);

drop table if exists alleleset;
create table alleleset (
    id int primary key auto_increment,
    alleleset_binaryid tinyint,
    strain_id int not null, 
    chromosome_name varchar(100) default null,
    foreign key (strain_id) references strain(id)
);

drop table if exists plasmid;
create table plasmid (
    id int primary key auto_increment,
    name varchar(100) not null,
    expanded_name varchar(200) not null,
    source varchar(100),
    parent1 varchar(100) default null,
    parent2 varchar(100) default null,
    restriction_site varchar(100) default null,
    date date default null
);

drop table if exists allele_plasmid;
create table allele_plasmid (
    allele_id int,
    plasmid_id int,
    foreign key (allele_id) references allele(id),
    foreign key (plasmid_id) references plasmid(id)
);

drop table if exists alleleset_allele;
create table alleleset_allele (
    alleleset_id int,
    allele_id int,
    heterozygous boolean,
    foreign key (alleleset_id) references alleleset(id),
    foreign key (allele_id) references allele(id)
);

