#!/usr/bin/env python
"""
Performs basic cleaning of W&B dataset and saves results to W&B.
"""
import argparse
import logging

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Performs basic cleaning of data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="W&B raw dataset for basic preprocessing",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Cleaned dataset to be uploaded to W&B",
        required=True
    )

    parser.min_price(
        "--output_artifact", 
        type=float,
        help="Floor of location price for dataset filtering",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Ceiling of location price for dataset filtering",
        required=True
    )

    args = parser.parse_args()

    go(args)
