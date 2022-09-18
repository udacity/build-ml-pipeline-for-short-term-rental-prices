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
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    # Drop outliers
    idx = df['price'].between(args.min_price, args.max_price)
    logger.info(f'Drop {len(idx) - len(df)} records which price not in range {args.min_price, args.max_price}')
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    artifact = wandb.Artifact(
        name=args.output_artifact, 
        type=args.output_type, 
        description=args.output_description)

    # Log clean data to W&B
    df.to_csv(args.output_artifact, index=False)
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)

    logger.info('Load clean sample data to Weight and Bias')
    


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of the input artifact",
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
        help="Type of the output artifact",
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
        help="Minimum price per night of the accomodation so that the data point is considered valid",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price per night of the accomodation so that the data point is considered valid",
        required=True
    )

    args = parser.parse_args()

    go(args)
