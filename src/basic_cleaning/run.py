#!/usr/bin/env python
"""
Download the raw dataset from W&B and apply some basic data clearning, exporting the result to the new artifact
"""
import argparse
import logging
import wandb
import os

import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    logger.info("Artifact download")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    logger.info("Dropping the outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Last_review to datetime type convertion")
    df['last_review'] = pd.to_datetime(df['last_review'])
    
    # leave out the rows that are not in the exact geolocation
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info("saving the output artifact")
    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    logger.info("Creating artifact")
    artifact = wandb.Artifact(
        name=args.output_artifact, 
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file(filename)
    logger.info("Artifact logging")
    run.log_artifact(artifact)

    # os.remove(filename)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data_cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Detailed name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Output artifact name",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Artifact description",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum threshold for cleaning outliers",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum threshold for cleaning outliers",
        required=True
    )

    args = parser.parse_args()

    go(args)
