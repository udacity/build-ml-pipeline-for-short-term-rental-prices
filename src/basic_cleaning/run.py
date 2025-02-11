#!/usr/bin/env python
"""
This script is to provide basic cleanup on dataset.
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

    # get input_artifact
    logging.info(f"INFO: Load input file {args.input_artifact} for basic cleaning")
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    input_dataset = pd.read_csv(artifact_local_path, index_col="id")

    # clean data
    logging.info(f"INFO: Filter out outliers and nulls with filter {args.min_price} and {args.max_price}")
    idx = input_dataset['price'].between(args.min_price, args.max_price)
    input_dataset = input_dataset[idx].copy()
    logging.info("INFO: Basic cleaning is completed")
    
    # convert datetime 
    logging.info(f"INFO: Convert last_review from string to datetime")
    input_dataset['last_review'] = pd.to_datetime(input_dataset['last_review'])
    logging.info("INFO: last_review column datetime conversion is completed")

    # save the dataset
    tmp_artifact_path = os.path.join(args.tmp_directory, args.output_artifact)
    input_dataset.to_csv(tmp_artifact_path)
    logging.info(f"INFO: input dataset is saved to local tmp path {tmp_artifact_path}")
    
    # create an artifact
    artifact = wandb.Artifact(
        args.output_artifact, 
        type=args.output_type, 
        description=args.output_description
    )

    artifact.add_file(tmp_artifact_path)
    run.log_artifact(artifact)
    artifact.wait()

    run.finish()
    logging.info("INFO: cleaned dataset is uploaded to w&b")
   
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="basic data cleaning")

    parser.add_argument(
        "--tmp_directory", 
        type=str, 
        help="Local temp directory to save cleaned dataset", 
        required=True
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Input csv data to be cleaned up.",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str, 
        help="Cleaned csv dataset name to be uploaded to w&b",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str, 
        help="clean data", 
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str, 
        help="A cleaned dataset that outliers and nulls are removed.",
        required=False,
        default="A cleaned dataset that outliers and nulls are removed."
    )

    parser.add_argument(
        "--min_price", 
        type=float, 
        help="Minimum price that is used to filter out outliers.",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float, 
        help="Maximum price that is used to filter out outliers.",
        required=True
    )
    
    args = parser.parse_args()

    go(args)
