#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path)

    # Perform cleaning steps
    logger.info("Limiting prices")

    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save cleaned data to new artifact
    df.to_csv("clean_sample.csv", index=False)

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
        type= str,
        help= "Input CSV file from W&B",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type= str,
        help="Cleaned output file",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type= str,
        help="Cleaned file",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type= str,
        help="Raw sample file has been cleaned",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type= float,
        help="Minimal price to filter for",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type= float,
        help="Maximum price to filter for",
        required=True
    )


    args = parser.parse_args()

    go(args)
