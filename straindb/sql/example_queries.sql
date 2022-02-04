use heimanlab;

-- Example Queries

-- 1. All strains that have plasmids X and Y but not plasmid Z

set @plasmidX = 'pCY118';
set @plasmidY = 'pCY168';
set @plasmidZ = 'pCY155';

select distinct s1.name
  from strain s1
  join strain s2 on s1.id = s2.id
  join strain s3 on s3.id = s2.id    
  join strain_plasmid sp1 on s1.id = sp1.strain_id
  join strain_plasmid sp2 on s2.id = sp2.strain_id
  join strain_plasmid sp3 on s3.id = sp3.strain_id
  join plasmid p1 on p1.id = sp1.plasmid_id
  join plasmid p2 on p2.id = sp2.plasmid_id
  left outer join plasmid p3 on p3.id = sp3.plasmid_id and p3.name = @plasmidZ    
  where p1.name = @plasmidX
    and p2.name = @plasmidY
    and p3.name is null;

-- Query result: CHB2524


-- 2. Strains that have a mutation on gene X (i.e., strains whose genotype mentions gene X)

set @gene = 'apa-2';

select s.name
  from strain s
  join alleleset ast on ast.strain_id = s.id
  join alleleset_allele aa on aa.alleleset_id = ast.id
  join allele a on a.id = aa.allele_id
  join gene g on g.id = a.gene_id
  where g.name = @gene;

-- Query results:
-- CHB3342
-- CHB3513
-- CHB3514


-- 3. Strains with mutant alleles X AND Y (i.e., strains whose genotype mentions allele X and allele Y)

set @alleleX = 'p808';
set @alleleY = 'hmn12';

select s1.name
  from strain s1
  join strain s2 on s2.id = s1.id
  join alleleset ast1 on ast1.strain_id = s1.id
  join alleleset ast2 on ast2.strain_id = s2.id
  join alleleset_allele aa1 on aa1.alleleset_id = ast1.id
  join alleleset_allele aa2 on aa2.alleleset_id = ast2.id
  join allele a1 on a1.id = aa1.allele_id  
  join allele a2 on a2.id = aa2.allele_id
  where a1.name = @alleleX and a2.name = @alleleY;
  
-- Query results (13 strains):
-- CHB2315
-- CHB2314
-- CHB2549
-- CHB2550
-- CHB2548
-- CHB2570
-- CHB2569
-- CHB2571
-- CHB2612
-- CHB2606
-- CHB2610
-- CHB2611
-- CHB2607


-- 4. Strains with mutant allele X but NOT Y

set @alleleX = 'mIn1';
set @alleleY = 'ia4';

select distinct s1.name
  from strain s1
  join strain s2 on s1.id = s2.id
  join alleleset ast1 on s1.id = ast1.strain_id
  join alleleset ast2 on s2.id = ast2.strain_id
  join alleleset_allele aa1 on aa1.alleleset_id = ast1.id
  join alleleset_allele aa2 on aa2.alleleset_id = ast2.id  
  join allele a1 on a1.id = aa1.allele_id  
  left outer join allele a2 on a2.id = aa2.allele_id and a2.name = 'ia4'
  where a1.name = @alleleX and a2.name is null;

-- Query results (11 strains):
-- CHB150
-- CHB214
-- CHB756
-- CHB757
-- CHB758
-- CHB824
-- CHB828
-- CHB2344
-- CHB2338
-- CHB2337
-- CHB2339


-- 5. Strains with mutant allele X AND plasmid Y

set @alleleX = 'oyIs44';
set @plasmidY = 'pMH339';

select s.name
  from strain s
  join alleleset ast on ast.strain_id = s.id
  join alleleset_allele aa on aa.alleleset_id = ast.id
  join allele a on a.id = aa.allele_id and a.name = @alleleX
  join strain_plasmid sp on sp.strain_id = s.id
  join plasmid p on p.id = sp.plasmid_id and p.name = @plasmidY;
 
-- Query results (271 strains): CHB6, CHB13, CHB26, CHB38, CHB42, CHB45, ...


