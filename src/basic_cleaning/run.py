#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning,
exporting the result to a new artifact.
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def drop_outliers(df: pd.DataFrame,
                  min_price: float,
                  max_price: float) -> pd.DataFrame:
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    return df


def go(args):
    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info(f"Loading {args.input_artifact} from W&B.")
    artifact_local_path = run.use_artifact(args.input_artifact).file()


    ######################
    # YOUR CODE HERE     #
    ######################
    df = pd.read_csv(artifact_local_path)
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    df = drop_outliers(df, min_price=min_price, max_price=max_price)
    # Convert last_review to datetime\n"
    df['last_review'] = pd.to_datetime(df['last_review'])
    ds_name = "clean_sample.csv"
    df.to_csv(ds_name, index=False)
    logger.info(f"Stored clean data into {ds_name}")

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(ds_name)
    run.log_artifact(artifact)
    logger.info(f"Uploaded {ds_name} to W&B.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This steps cleans the data")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name of the input artifact in W&B",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price per night",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price per night",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name of the output artifact in W&B",
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

    args = parser.parse_args()

    go(args)
