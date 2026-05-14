#!/usr/bin/env python
"""
Download the raw dataset from W&B, apply basic cleaning, and upload the result as a new artifact.
"""
import argparse
import logging
import os

import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info("Downloading input artifact %s", args.input_artifact)
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    logger.info("Dropping price outliers (keep %s <= price <= %s)", args.min_price, args.max_price)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Restrict to the NYC bounding box so the proper_boundaries test holds for
    # future samples (e.g. sample2.csv) that contain out-of-area rows.
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    output_path = "clean_sample.csv"
    df.to_csv(output_path, index=False)

    logger.info("Uploading %s to W&B as %s", output_path, args.output_artifact)
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(output_path)
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning step")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name of the input W&B artifact (e.g. sample.csv:latest)",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the cleaned output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type of the output artifact",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description for the output artifact",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price to consider (rows below this are dropped)",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price to consider (rows above this are dropped)",
        required=True,
    )

    args = parser.parse_args()

    go(args)
