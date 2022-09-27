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

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Downloading artifact...")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    logger.info("Reading artifact...")
    df = pd.read_csv(artifact_path)

    logger.info("Dropping duplicates...")
    df = df.drop_duplicates().reset_index(drop=True)

    logger.info("Removing outliers...")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    df['last_review'] = pd.to_datetime(df['last_review'])

    logger.info("Saving artifact...")
    df.to_csv(args.output_artifact, index=False)
    cleaned_artifact = wandb.Artifact(args.output_artifact,
                                      type=args.output_type, description=args.output_description,
                                      )
    cleaned_artifact.add_file(args.output_artifact)

    logger.info("Logging artifact...")
    run.log_artifact(cleaned_artifact)

    os.remove(args.output_artifact)
    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="input artifact name (*.csv)",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="output artifact name (*.csv)",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="type of the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="description of output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="minimum price - to remove outliers",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="maximum price - to remove outliers",
        required=True
    )

    args = parser.parse_args()

    go(args)
