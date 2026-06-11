#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import os
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info("Downloading artifact...")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    
    df = pd.read_csv(artifact_local_path)

    logger.info("Dropping duplicates...")
    df = df.drop_duplicates().reset_index(drop=True)

    logger.info("Feature engineering...")
    df['price'] = df['price'].fillna(0)
    df_filtered = df[df['price'].between(args.min_price, args.max_price, inclusive='both')]
    
    filename = "clean_sample.csv"
    df_filtered.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A very basic data cleaning"
    )

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully qualified name of the artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the produced artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the artifact to be produced",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=int,
        help="Minimum price to be filtered",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=int,
        help="Maximum price to be filtered",
        required=True
    )


    args = parser.parse_args()

    go(args)
