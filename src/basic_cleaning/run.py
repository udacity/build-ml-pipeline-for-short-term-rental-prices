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

    ######################
    # YOUR CODE HERE     #
    ######################
    #	1. Download the input artifact from W&B
    local_path = wandb.use_artifact("sample.csv:latest").file()
    df = pd.read_csv(local_path)
    
    # Basic cleaning
    df = df.drop_duplicates()
    df = df.dropna(subset=["price"])

    #   2.  Filtering outlier
    df = df[df["price"].between(args.min_price, args.max_price)]

    # Add this boundary filter
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)

    df = df[idx].copy()
    logger.info("Cleaned data has %s rows and %s columns", *df.shape)

    #   3. Save the cleaned DataFrame as clean_sample.csv
    df.to_csv("clean_sample.csv", index=False)

    #   4. Upload the artifact to W&B
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
        type=str,
        help="Fully qualified name for the input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Fully qualified name for the output artifact" ,
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type of the output artifact to be created",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the artifact to be created",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price to process",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price to process",
        required=True
    )


    args = parser.parse_args()

    go(args)
