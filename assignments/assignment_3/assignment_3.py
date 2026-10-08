import argparse
from Bio import SeqIO
import configparser
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String
from sqlalchemy.sql import text

# Sets up tables
metadata_obj = sqlalchemy.MetaData()
species_table = Table("species", metadata_obj,
                      Column("accession_number", String(50), primary_key=True, nullable=False),
                      Column("species_name", String(300), nullable=False),
                      Column("taxon_id", Integer, nullable=False),
                      Column("genome_size", Integer, nullable=False),
                      Column("gene_count", Integer, nullable=False),
                      Column("protein_count", Integer, nullable=False))

protein_table = Table("proteins", metadata_obj,
                      Column("id", Integer, primary_key=True, autoincrement=True),
                      Column("protein_id", String(100), nullable=False),
                      Column("product_name", String(200)),
                      Column("location", String(50), nullable=False),
                      Column("gene_name", String(50), nullable=True),
                      Column("locus_tag", String(50), nullable=False))

go_table = Table("go_terms", metadata_obj,
                 Column("id", Integer, primary_key=True, autoincrement=True),
                 Column("GO_term", String(30), nullable=False),
                 Column("protein_id", String(100), nullable=False))

ec_table = Table("ec_terms", metadata_obj,
                 Column("id", Integer, primary_key=True, autoincrement=True),
                 Column("ec_id", String(30), nullable=False),
                 Column("protein_id", String(100), nullable=False))


def argument_parsing():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--genbank_file", help="the path to the genbank file")
    parser.add_argument("-c", "--config_file", help="the path to the config file")
    args = parser.parse_args()
    return args

def insert_species_data(engine, data):
    """Inserts species data into the database"""
    query = text("INSERT INTO species (accession_number, species_name, "
                 "taxon_id, genome_size, gene_count, protein_count) "
                 "VALUES (:accession_number, :species_name, :taxon_id, :genome_size, :gene_count, :protein_count)")
    conn = engine.connect()
    conn.execute(query, data)
    conn.commit()

def insert_protein_data(engine, data):
    """Inserts protein data into the database"""
    query = text("INSERT INTO proteins (protein_id, product_name, location, locus_tag, gene_name) "
                 "VALUES (:protein_id, :product_name, :location, :locus_tag, :gene_name)")
    conn = engine.connect()
    conn.execute(query, data)
    conn.commit()

def insert_go_data(engine, data):
    """Inserts GO data into the database"""
    query = text("INSERT INTO go_terms (GO_term, protein_id) "
                 "VALUES (:GO_term, :protein_id)")
    conn = engine.connect()
    conn.execute(query, data)
    conn.commit()

def insert_ec_data(engine, data):
    """Inserts ec data into the database"""
    query = text("INSERT INTO ec_terms (ec_id, protein_id) "
                 "VALUES (:ec_id, :protein_id)")
    conn = engine.connect()
    conn.execute(query, data)
    conn.commit()

def extract_features(record, genbank_info):
    """
    Within the Genbank file, gather the feature information.
    :param record: GenBank record
    :param genbank_info: dictionary with already found genbank info
    :return: list of found proteins, list of found ec numbers, list of go terms
    """
    protein_list, protein_dict = [], {}
    ec_numbers, go_terms = [], []
    gene_counts, protein_counts = 0, 0
    for feature in record.features:
        if feature.type == "source":
            for db_xref in feature.qualifiers.get("db_xref", []):
                if db_xref.startswith("taxon:"):
                    genbank_info["taxon_id"] = int(db_xref.split(":")[1])
        if feature.type == "gene":
            gene_counts += 1
        if feature.type == "CDS":
            protein_counts += 1
            protein_id = feature.qualifiers.get("protein_id", [None])[0]
            if protein_id is not None:
                protein_dict["gene_name"] = feature.qualifiers.get("gene", ["None"])[0]
                protein_dict["locus_tag"] = feature.qualifiers.get("locus_tag", ["None"])[0]
                protein_dict["product_name"] = feature.qualifiers.get("product", ["None"])[0]
                protein_dict["protein_id"] = protein_id
                protein_dict["location"] = str(feature.location)
                # Get the EC and GO terms
                for ec in feature.qualifiers.get("EC_number", []):
                    if ec is not None and protein_dict["protein_id"] is not None:
                        ec_numbers.append({"protein_id": protein_dict["protein_id"], "ec_id": ec})

                for db_xref in feature.qualifiers.get("db_xref", []):
                    if db_xref.startswith("GO:"):
                        go_terms.append({"protein_id":protein_dict["protein_id"], "GO_term":db_xref.split(":")[1]})

                protein_list.append(protein_dict)
                protein_dict = {}
    return protein_list, ec_numbers, go_terms, gene_counts, protein_counts

def extract_genome_info(record):
    """
    Find the easy to gather genbank record information.
    """
    genbank_info = {}
    genbank_info["species_name"] = record.annotations.get("organism")
    genbank_info["accession_number"] = record.id
    genbank_info["genome_size"] = len(record.seq)

    protein_list, ec, go, gene_counts, protein_counts = extract_features(record, genbank_info)
    genbank_info["protein_count"] = protein_counts
    genbank_info["gene_count"] = gene_counts
    return genbank_info, protein_list, ec, go

def set_up_database(config):
    """
    Sets up a database connection
    params:
    config: the read config file
    returns:
    the engine that manages the connection to the database
    """
    # Database connection setup
    db = config["client"]
    url = URL.create("mysql+mysqldb",
      username=db["user"],password=db["password"],
      host=db["host"],port=int(db["port"]),database=db["database"])
    return create_engine(url)

def main():
    args = argument_parsing()
    config = configparser.ConfigParser()
    config.read(args.config_file)
    engine = set_up_database(config)
    #Sets tables up
    metadata_obj.create_all(engine)
    for record in SeqIO.parse(args.genbank_file, "genbank"):
        genome_info, protein_info, ec_info, go_info = extract_genome_info(record)
        insert_species_data(engine, genome_info)
        if protein_info:
            insert_protein_data(engine, protein_info)
        if go_info:
            insert_go_data(engine, go_info)
        if ec_info:
            insert_ec_data(engine, ec_info)

if __name__ == "__main__":
    if sqlalchemy.__version__.startswith('1.4'):
        from sqlalchemy.engine import make_url, URL
    elif sqlalchemy.__version__.startswith('2'):
        from sqlalchemy.engine.url import make_url, URL
    main()
