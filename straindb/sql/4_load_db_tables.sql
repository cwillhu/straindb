
-- Error tables
drop table if exists allele_missing_from_staging_allele_table;
create table allele_missing_from_staging_allele_table (
  strain_original_line_number int,
  strain_name varchar(100),
  allele_name varchar(100)
) engine = MyISAM; -- use MyISAM so error tables are unaffected by rollbacks

drop table if exists plasmid_missing_from_staging_plasmid_table;
create table plasmid_missing_from_staging_plasmid_table (
  strain_original_line_number int,
  strain_name varchar(100),
  allele_original_line_number int,
  allele_name varchar(100),
  plasmid_name varchar(100)
) engine = MyISAM;

-- Load strain, allele, alleleset, alleleset_allele, allele_plasmid, plasmid and gene tables
-- using staging_strain, staging_strain_allele, staging_allele and staging_plasmid tables
drop procedure if exists etl_tables;
delimiter //
create procedure etl_tables()
begin

  select @nrows_strain := max(id) from staging_strain;
  update staging_allele set processed = 0;
  update staging_strain_allele set processed = 0;  
  set @strain_counter = 1;
  
  strain_loop: while @strain_counter <= @nrows_strain do

    start transaction;

    select @strain_name := strain_name from staging_strain where id = @strain_counter;

    while exists (select * from staging_strain_allele where processed = 0 and strain_name = @strain_name) do

      select
        @staging_strain_allele_id    := id,
        @strain_original_line_number := strain_original_line_number,
        @chromosome                  := chromosome,
        @alleleset_binaryid          := alleleset_binaryid,
        @allele_name                 := allele_name,
        @gene_name                   := gene_name,
        @heterozygous                := heterozygous,
        @other_names                 := other_names,
        @source                      := source,
        @comment                     := comment
      from staging_strain_allele
      where strain_name = @strain_name and processed = 0 limit 1;

      -- Add strain to strain table, if needeed
      if not exists (select * from strain where name = @strain_name) then
        insert into strain (name, other_names, source, comment) values (@strain_name, @other_names, @source, @comment);
      end if;
      select @strain_id := id from strain where name = @strain_name;

      -- Add allele, if exists (i.e., a genotype with an allele was specified for this strain)
      if @allele_name is not null then

        -- Rollback if allele not in staging_allele
        if not exists (select * from staging_allele where name = @allele_name) then
          -- Add allele to error table
          insert into allele_missing_from_staging_allele_table values (@strain_original_line_number, @strain_name, @allele_name);
          rollback;
          set @strain_counter = @strain_counter + 1;
          iterate strain_loop;
        end if;

        -- Add alleleset to alleleset table, if needed
        if not exists (
            select * from alleleset
            where alleleset_binaryid = @alleleset_binaryid and strain_id = @strain_id and chromosome_name <=> @chromosome
          ) then      
          insert into alleleset (alleleset_binaryid, strain_id, chromosome_name) values (@alleleset_binaryid, @strain_id, @chromosome);
        end if;
      
        -- Get alleleset_id
        select @alleleset_id := id from alleleset
          where alleleset_binaryid = @alleleset_binaryid and strain_id = @strain_id and chromosome_name <=> @chromosome;

        -- Add allele to allele table, gene to gene table, plasmids to plasmid table, if needed
        if not exists (select * from allele where name = @allele_name) then

          -- Get this allele's comment and allele_original_line_number from staging_allele table      
          select
	    @allele_original_line_number := allele_original_line_number,
	    @allele_comment := comment,
	    @allele_type := allele_type
            from staging_allele where name = @allele_name limit 1;

          -- If gene_name is null, try to get allele's gene_name from staging_allele table
          if @gene_name is null then
            select @gene_name := gene_name from staging_allele where name = @allele_name limit 1;
          end if;

          -- Add gene to gene_table, if needed
          if @gene_name is not null and not exists (select * from gene where name = @gene_name) then
            insert into gene (name) values (@gene_name);
          end if;

          -- Get gene_id
          select @gene_id := id from gene where name = @gene_name; -- NULL if gene_name is NULL

          -- Add allele to allele table
          insert into allele (name, allele_type, gene_id, comment) values (@allele_name, @allele_type, @gene_id, @allele_comment);  

          -- Get allele_id
          select @allele_id := id from allele where name = @allele_name;

          -- Add this allele's plasmids to plasmid table
          while exists (select * from staging_allele where name = @allele_name and processed = 0) do

            -- Get a plasmid name to process
            select @plasmid_name := plasmid_name, @staging_allele_id := id from staging_allele where name = @allele_name and processed = 0 limit 1;

            if @plasmid_name is not null then
	    
              -- Check plasmid_name exists in staging_plasmid table
              if not exists (select * from staging_plasmid where name = @plasmid_name) then

                -- Add plasmid to error table
                insert into plasmid_missing_from_staging_plasmid_table
                  values (@strain_original_line_number, @strain_name, 
                          @allele_original_line_number, @allele_name,
                          @plasmid_name);
                rollback;
                set @strain_counter = @strain_counter + 1;
                iterate strain_loop;
              end if;

              -- Get plasmid attributes from staging_plasmid (expanded_name is non-null)
              select
                @expanded_name    := expanded_name,
                @plasmid_source   := source,
                @parent1          := parent1,
                @parent2          := parent2,
                @restriction_site := restriction_site,
                @datestr          := datestr
              from staging_plasmid where name = @plasmid_name;	  

              -- Add plasmid to plasmid table, if needed
              if not exists (select * from plasmid where name = @plasmid_name) then
                insert into plasmid (name, expanded_name, source, parent1, parent2, restriction_site, date)
                  values (@plasmid_name, @expanded_name, @plasmid_source, @parent1, @parent2, @restriction_site, @datestr);
              end if;

              -- Get id of plasmid 
              select @plasmid_id := id from plasmid where name = @plasmid_name and expanded_name = @expanded_name;
	    
              -- Add entry to allele_plasmid table, if needed
              if not exists (select * from allele_plasmid where allele_id = @allele_id and plasmid_id = @plasmid_id) then
                insert into allele_plasmid (allele_id, plasmid_id) values (@allele_id, @plasmid_id);
              end if;

            end if; -- if @plasmid_name is not null

            update staging_allele set processed = 1 where id = @staging_allele_id;

          end while;

        end if;  -- if not exists @allele_name in allele table

        -- Now that allele is assured to be in allele table, get allele_id
        select @allele_id := id from allele where name = @allele_name;      

        -- Add entry to alleleset_allele for this allele
        insert into alleleset_allele (alleleset_id, allele_id, heterozygous)
          values (@alleleset_id, @allele_id, @heterozygous);

      end if;  -- if @allele_name is not null

      update staging_strain_allele set processed = 1 where id = @staging_strain_allele_id;
      
    end while;  -- strain_allele loop

    commit;

    set @strain_counter = @strain_counter + 1;

  end while; -- strain loop
  
end //
delimiter ;  

-- run ETL of database tables
set autocommit = 0;
set SQL_SAFE_UPDATES = 0;

call etl_tables();

set autocommit = 1;
