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

    run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning:{args.input_artifact}")
    run.config.update(args)

    logger.info(f"Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()
    
    df = pd.read_csv(artifact_local_path)
    # logger.info(f"Data loaded with shape: {df.shape}")

    # Filter data using min_price and max_price
    min_price = float(args.min_price)
    max_price = float(args.max_price)
    logger.info(f"Filtering data between prices {min_price} and {max_price}")
    df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]

    # Save cleaned data
    df.to_csv("clean_sample.csv", index=False)
    logger.info(f"Saved cleaned data to clean_sample.csv")


    artifact = wandb.Artifact(
    args.output_artifact,
    type=args.output_type,
    description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
import wandb

# Initialize W&B run
run = wandb.init(project="nyc_airbnb", job_type="basic_cleaning")

# Replace with your actual artifact name
artifact = run.use_artifact("sample.csv:v0")  # e.g., "sample.csv:latest"

# Download and get the local file path
artifact_local_path = artifact.file()

# You can now load it with pandas
import pandas as pd
df = pd.read_csv(artifact_local_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully-qualified name for the input artifact (e.g. sample.csv:latest)",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the output artifact (e.g. clean_sample.csv)",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Type for the output artifact (e.g. clean_sample)",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum acceptable price (10)",
        required=True
    )


    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum acceptable price (350)",
        required=True
    )



    args = parser.parse_args()

    go(args)
