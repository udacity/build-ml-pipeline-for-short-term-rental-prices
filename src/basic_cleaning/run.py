#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd
import os
import hydra


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    """
    Basic cleaning
    Remove outliner by input min proce and max price.
    Change last_review to datetime. 
    """

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    input = args.input_artifact

    run = wandb.init(job_type="basic_cleaning")

    local_path = wandb.use_artifact(input).file()
    df = pd.read_csv(local_path)

    min_price = args.min_price
    max_price = args.max_price

    logger.info(f"Dataset price outliers removal outside range: {min_price} - {max_price}")
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Convert last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])


    logger.info("Clean lat, long")
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()


    logger.info("Save Output as clean_sample.csv")
    df.to_csv("clean_sample.csv",index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="nyc_airbnb dataset name as CSV format",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="clean nyc_airbnb dataset name as CSV format",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Dataframe",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Cleaned dataset by filter price outliner and convert last review to datetime.",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price limit",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price limit",
        required=True
    )


    args = parser.parse_args()

    go(args)
