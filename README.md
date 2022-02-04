
## StrainDB

Python >= 3.6 is recommended.

- Download straindb, navigate to package directory and install locally:

  python3 -m pip install -e .

- Edit straindb/config.yaml to set output directory, input file paths

- Filter invalid rows and columns from original CSVs:

  python3 straindb/filter_csv.py

- Normalize strain and allele tables:

  python3 straindb/normalize_csv.py

- Execute ETL scripts 0 through 5 in straindb/sql (after editing absolute paths in 2_load_staging_tables.sql)

- Execute example queries in straindb/sql/example_queries.sql

