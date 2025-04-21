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
    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("💿 Running basic cleaning...")
    try:
        run = wandb.init(job_type="basic_cleaning")
        run.config.update(args)
        run = wandb.init(project="nyc_airbnb", group="eda", save_code=True)
        artifact_local_path = run.use_artifact(args.input_artifact).file()
        df = pd.read_csv(artifact_local_path)

        # Drop outliers
        logger.info("🧹 Dropping outliers...")
        idx = df['price'].between(args.min_price, args.max_price)
        df = df[idx].copy()

        # Convert last_review to datetime
        df['last_review'] = pd.to_datetime(df['last_review'])
        # Handle missing reviews_per_month 
        df['reviews_per_month'] = df['reviews_per_month'].fillna(0)
        # Handle missing number_of_reviews 
        df['number_of_reviews'] = df['number_of_reviews'].fillna(0)
        # Handle missing availability_365 
        df['availability_365'] = df['availability_365'].fillna(0)

        logger.info("🗳️ Converting to .csv...")
        df.to_csv("clean_sample.csv", index=False)

        artifact = wandb.Artifact(
            args.output_artifact,
            type=args.output_type,
            description=args.output_description,
        )

        artifact.add_file("clean_sample.csv")
        run.log_artifact(artifact)

        logger.info("👍 Basic data cleaning done!")
        run.finish()
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="output_artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="output_type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="output_description",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="min_price",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="max_price",
        required=True
    )


    args = parser.parse_args()

    go(args)
