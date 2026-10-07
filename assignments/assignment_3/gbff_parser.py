import argparse
import re
import configparser
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text

def argument_parsing():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--genbank_file", help="the path to the genbank file")
    parser.add_argument("-c", "--config_file", help="the path to the config file")
    args = parser.parse_args()
    return args

def parse_gbff(path):
    """
    Parses the genbank file and extract the information as described in the exercise
    params:
    path: the path to the genbank file
    returns:
    a dictionary with genbank info
    """
    gb_information = {}
    gene_count, protein_count = 0, 0
    taxid_pattern = re.compile(r"^\s+/db_xref=\"taxon:(\d+)\"")
    with open(path, "r") as handle:
        for line in handle:
                if line.startswith("LOCUS"):
                    genome_size = int(line.split()[2])
                    gb_information["genome_size"] = genome_size
                elif line.startswith("VERSION"):
                    gb_information["version"] = line.split()[1]
                elif line.startswith("  ORGANISM"):
                    gb_information["organism"] = line[10:].strip()
                elif line.startswith("     gene"):
                    gene_count += 1
                elif line.startswith("     CDS"):
                    protein_count += 1
                elif taxid_pattern.search(line):
                    gb_information["taxon_id"] = taxid_pattern.search(line).group(1)
        gb_information["gene_count"] = gene_count
        gb_information["protein_count"] = protein_count
    return gb_information

def set_up_database(config_path):
    """
    Sets up a database connection
    params:
    config_path: the path to the config file
    returns:
    the engine that manages the connection to the database
    """
    # Database connection setup
    config = configparser.ConfigParser()
    config.read(config_path)
    db = config["client"]
    url = URL.create("mysql+mysqldb",
      username=db["user"],password=db["password"],
      host=db["host"],port=int(db["port"]),database=db["database"])
    engine = create_engine(url)
    return engine

if __name__ == "__main__":
    if sqlalchemy.__version__.startswith('1.4'):
        from sqlalchemy.engine import make_url, URL
    elif sqlalchemy.__version__.startswith('2'):
        from sqlalchemy.engine.url import make_url, URL
    args = argument_parsing()
    parts = parse_gbff("genomic.gbff")
    set_up_database(args.config_file)
