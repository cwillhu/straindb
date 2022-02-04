-- Create views to simplify queries

-- Additional error "table": view of alleles with 'other' allele_type
drop view if exists allele_no_allele_type;
create view allele_no_allele_type as
  select * from allele where allele_type = 'other';

-- Create view strain_plasmid (mapping from strains to plasmids)
drop view if exists strain_plasmid;
create view strain_plasmid as
  select s.id as strain_id, p.id as plasmid_id
    from strain s
    join alleleset ast on ast.strain_id = s.id
    join alleleset_allele aa on aa.alleleset_id = ast.id
    join allele a on a.id = aa.allele_id
    join allele_plasmid ap on ap.allele_id = a.id
    join plasmid p on p.id = ap.plasmid_id;

-- Create convenience view of strains 
drop view if exists strain_view;
create view strain_view as
  select
    s.id as strain_id,
    s.name as strain_name,
    group_concat(a.name separator ', ') as allele_names,
    group_concat(ast.chromosome_name separator ', ') as chromosome_names,
    group_concat(p.name  separator ', ') as plasmids,
    group_concat(p.expanded_name  separator ', ') as plasmid_expanded_names,
    group_concat(g.name  separator ', ') as gene_names,    
    s.source as strain_source
  from strain s
  left outer join alleleset ast on ast.strain_id = s.id
  left outer join alleleset_allele aa on aa.alleleset_id = ast.id  
  left outer join allele a on a.id = aa.allele_id
  left outer join allele_plasmid ap on ap.allele_id = a.id
  left outer join plasmid p on p.id = ap.plasmid_id
  left outer join gene g on g.id = a.gene_id
  group by
    s.id,
    s.name,
    s.source;
  
