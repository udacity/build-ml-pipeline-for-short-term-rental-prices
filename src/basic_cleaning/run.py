#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
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

    logger.info(f"Downloading {args.input_artifact} ...")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    dataframe = pd.read_csv(artifact_path)

    min_price = args.min_price
    max_price = args.max_price
    logger.info('Applying min/max outlier detection on price column')
    try:
        # Outlier drop on price
        idx = dataframe['price'].between (min_price, max_price)
    except TypeError as err:
        logger.error(err)
        logger.error('Min price and Max Price are not numbers')
        raise TypeError(err)

    outlier_df = dataframe[idx].copy ()

    # Convert last_review to datetime
    outlier_df['last_review'] = pd.to_datetime (outlier_df['last_review'])
    outlier_df.to_parquet(args.output_artifact)

    logger.info(f'Storing file as {args.output_artifact}...')

    # Storing the dataset
    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(args.output_artifact)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of the input artifact to be cleaned",
        required=True
    )
    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of the output artifact to be saved",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="File type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price threshold to clean outliers",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price threshold to clean outliers",
        required=True
    )

    args = parser.parse_args()

    go(args)
