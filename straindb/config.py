''' Parse YAML config file '''

import yaml
from pathlib import Path

# Read config file
config_filepath = Path(__file__).parent.joinpath('config.yaml')
with open(config_filepath) as f:
    config = yaml.load(f, Loader=yaml.Loader)

rawCSV = {}
rawCSV['allele']  = Path(config['raw_csv']['allele'])
rawCSV['plasmid'] = Path(config['raw_csv']['plasmid'])
rawCSV['strain']  = Path(config['raw_csv']['strain'])
              
output_directory = Path(config['output_directory'])

