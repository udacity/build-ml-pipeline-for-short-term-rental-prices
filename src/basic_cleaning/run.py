#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the
result to a new artifact
"""
import argparse
import logging
import pandas as pd
import wandb
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):
    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    run.config.update(args)

    logger.info("Load artifact")
    local_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)

    logger.info("Drop outliers")
    idx = df['price'].between(args.min_price, args.max_price)
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info("Convert last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info("Save cleaned data as csv")
    df.to_csv(args.output_artifact, index=False)

    logger.info("Upload csv to W&B")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    os.remove(args.output_artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Path to input artifact in W&B",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Path to output artifact in W&B",
        required=True,
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type of output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of output artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum accepted price",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum accepted price",
        required=True
    )


    args = parser.parse_args()

    go(args)
