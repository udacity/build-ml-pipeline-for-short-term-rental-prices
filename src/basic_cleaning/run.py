#!/usr/bin/env python
"""
Download the raw dataset artifact from Weights & Biases, perform basic data cleaning
(price outlier removal, date parsing, geographic boundary filtering), and upload the
cleaned dataset as a new artifact.
"""
import argparse
import logging

import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# Proper geographic boundaries for properties in and around New York City. Rows
# outside of this box are considered bad data points (e.g. data entry errors) and
# are dropped. Keeping this in sync with src/data_check/test_data.py::test_proper_boundaries.
NYC_LONGITUDE_RANGE = (-74.25, -73.50)
NYC_LATITUDE_RANGE = (40.5, 41.2)


def go(args: argparse.Namespace) -> None:
    """
    Run the basic_cleaning step: fetch the raw artifact, clean it, and log the
    cleaned result as a new W&B artifact.

    :param args: Parsed command line arguments. See the ``__main__`` section
        below for the full list of expected attributes.
    """
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info("Downloading artifact %s", args.input_artifact)
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    logger.info("Dropping price outliers outside [%s, %s]", args.min_price, args.max_price)
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Converting last_review to datetime")
    df["last_review"] = pd.to_datetime(df["last_review"])

    logger.info(
        "Dropping rows outside of the proper NYC geographic boundaries "
        "(longitude in %s, latitude in %s)",
        NYC_LONGITUDE_RANGE,
        NYC_LATITUDE_RANGE,
    )
    idx = df["longitude"].between(*NYC_LONGITUDE_RANGE) & df["latitude"].between(*NYC_LATITUDE_RANGE)
    df = df[idx].copy()

    logger.info("Saving cleaned dataframe to %s", args.output_artifact)
    df.to_csv("clean_sample.csv", index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    logger.info("Artifact %s logged successfully", args.output_artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Perform basic cleaning on the raw dataset")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name of the raw input artifact to download from W&B",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the cleaned output artifact that will be uploaded to W&B",
        required=True,
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type to assign to the output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="A free-text description of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum accepted price. Rows with a price below this value are dropped",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum accepted price. Rows with a price above this value are dropped",
        required=True,
    )

    args = parser.parse_args()

    go(args)
