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

    logger.info("Trying to download data")
    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    logger.info("Data downloaded")
    ######################
    # YOUR CODE HERE     #
    ######################

    logger.info("Performing Preprocessing")
    df = pd.read_csv(artifact_local_path)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info("Preprocessing done, saving and uploading to W&B")
    df.to_csv("clean_sample.csv", index=False)
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    logger.info("Data Stored in W&B, finishing component")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=" A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='name of the input artifact',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='name of the output artifact',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='type of the output artifact',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='description of the output artifact',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='minimum available price',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='maximum available price',
        required=True
    )


    args = parser.parse_args()

    go(args)
