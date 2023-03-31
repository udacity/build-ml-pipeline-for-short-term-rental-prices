#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
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

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Downloading artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Reading artifact")
    df = pd.read_csv(artifact_local_path)
    logger.info("Artifact read")

    logger.info("Dropping outliers between %f and %f", args.min_price, args.max_price)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Convert last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info("Ensuring that the longitude and latitude are correct")
    idx = (
        df['longitude'].between(args.min_longitude, args.max_longitude) & 
        df['latitude'].between(args.min_latitude, args.max_latitude)
        )
    
    logger.info("Saving locally")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Uploading artifact")
    artifact = wandb.Artifact(
        args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file('clean_sample.csv')
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact",
        required=True
    )

    parser.add_argument(
        "--artifact_name", 
        type=str,
        help="Name for the output artifact",
        required=True
    )

    parser.add_argument(
        "--artifact_type", 
        type=str,
        help="Output artifact type.",
        required=True
    )

    parser.add_argument(
        "--artifact_description", 
        type=str,
        help="A brief description of this artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price to filter",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price to filter",
        required=True
    )

    parser.add_argument(
        "--min_longitude",
        type=float,
        help="Minimum longitude to filter",
        required=True
    )

    parser.add_argument(
        "--max_longitude",
        type=float,
        help="Maximum longitude to filter",
        required=True
    )

    parser.add_argument(
        "--min_latitude",
        type=float,
        help="Minimum latitude to filter",
        required=True
    )

    parser.add_argument(
        "--max_latitude",
        type=float,
        help="Maximum latitude to filter",
        required=True
    )


    args = parser.parse_args()

    go(args)
