#!/usr/bin/env python
"""
Performs basic cleaning of W&B dataset and saves results to W&B.
"""
import argparse
import logging

import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    # get artifact and put in df
    logger.info(f"Fetching input data artifact {args.input_artifact}")
    input_artifact = wandb.use_artifact(args.input_artifact)
    df = pd.read_csv(input_artifact.file())

    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    logger.info("Dropping outliers outside of {min_price} and \
        {max_price} boundaries")
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save and upload cleaned dataframe to csv
    df.to_csv(args.output_artifact, index=False)
    
    logging.info("Uploading cleaned csv")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Performs basic cleaning of data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="W&B raw dataset for basic preprocessing",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Cleaned dataset to be uploaded to W&B",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the preprocessed artfact displayed in W&B",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the preprocessed artfact displayed in W&B",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Floor of location price for dataset filtering",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Ceiling of location price for dataset filtering",
        required=True
    )

    args = parser.parse_args()

    go(args)
