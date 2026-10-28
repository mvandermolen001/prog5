import sys, argparse

sys.path.append('/opt/spark/python')
sys.path.append('/opt/spark/python/lib/py4j-0.10.9.7-src.zip')
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf


def argument_parsing():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--input_file", help="the path to the input file")
    parser.add_argument("-c", "--code_book", help="the path to the code book")
    args = parser.parse_args()
    return args


def get_predict_columns(path):
    predictor_columns = []
    with open(path) as file:
        for line in file:
            line = line.strip()
            column_name, encoding, predict = line.split("\t")
            if "_pred" in column_name:
                predictor_columns.append(column_name)
        return predictor_columns


def main():
    """
    Main function that creates the dataframe and gets the answers to the assignments questions
    """
    args = argument_parsing()
    predictor_columns = get_predict_columns(args.code_book)
    spark = SparkSession.builder.appName('assignment5').master('local[16]').config('spark.executor.memory',
                                                                                   '128g').config('spark.driver.memory',
                                                                                                  '128g').getOrCreate()
    snp_df = spark.read.options(delimiter="\t", header=True, nanValue=".").csv(args.input_file)

    print("How many predictions per classifier:")
    counts = snp_df.select([sf.count_if(sf.col(c) != ".").alias(c) for c in predictor_columns])
    counts.show()
    print("Top five:")
    counts_dict = snp_df.select([sf.count_if(sf.col(c) != ".").alias(c) for c in predictor_columns]).first().asDict()
    top_5 = sorted(counts_dict.items(), key=lambda item: item[1], reverse=True)[:5]
    print(top_5)

    print("Dropping all predictor columns except top five:")
    keep_list = [key_item[0].removesuffix("_pred") for key_item in top_5]
    potential_drop_list = [column for column in snp_df.columns if
                           any(column.startswith(pred.strip("_pred")) for pred in predictor_columns)]
    drop_list = [column for column in potential_drop_list if
                 not any(column.startswith(top_column) for top_column in keep_list)]
    shortened_snp_df = snp_df.drop(*drop_list)
    print("Add the chr_pos column:")
    shortened_snp_df = shortened_snp_df.select("*", sf.concat_ws("_", *["#chr", "pos(1-based)"]).alias("chr_pos"))
    print("Position with the most associated predictions: ")
    shortened_snp_df.groupBy("chr_pos").count().sort(sf.desc("count")).show(1)
    print("Ensembl_proteinid with the most associated predictions:")
    shortened_snp_df.groupBy("Ensembl_proteinid").count().sort(sf.desc("count")).show(1)


if __name__ == "__main__":
    main()
