#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
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

    logger.info('Downloading artifact...')
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    
    logger.info('Creating dataframe..')
    df = pd.read_csv(artifact_local_path)
    
    logger.info('Cleaning data...')
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Drop data outside the wanted geolocation
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info('Uploading artifact...')
    csv_path = "clean_sample.csv"
    df.to_csv(csv_path, index=False)
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(csv_path)
    run.log_artifact(artifact)

    logger.info('Done! Cleaning up...')
    os.remove(csv_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='The location of the artifact to input',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='The location of the artifact to output',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='The type of the output',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='The description for the output',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='The rental minimum price',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='The rental maximum price',
        required=True
    )


    args = parser.parse_args()

    go(args)
