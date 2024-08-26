#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    # Drop the duplicates
    logger.info("Dropping duplicates and identify nulls")
    print(df.columns[df.isnull().any()])
    df.dropna(inplace=True) #drop rows with any nulls

    df = df.drop_duplicates().reset_index(drop=True)

    # Drop outliers and nulls
    logger.info("Dropping min max prices")
    df = df[(df['price'] >= args.min_price) & (df['price'] <= args.max_price)]

    filename = args.output_artifact

    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        filename,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This steps cleans the data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="name of input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="name of the artifact generated",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="type of the output",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="description of the output",
        required=False
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="min price",
        required=True
    )
    
    parser.add_argument(
        "--max_price", 
        type=float,
        help="max price",
        required=True
    )

    args = parser.parse_args()

    go(args)
