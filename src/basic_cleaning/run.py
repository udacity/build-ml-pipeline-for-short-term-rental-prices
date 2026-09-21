#!/usr/bin/env python
"""
performs basci cleaning
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
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    df.to_csv("clean_sample.csv", index=False)
    artifact = wandb.Artifact(args.output_artifact,
                type=args.output_type, description=args.output_description)
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)
    run.finish()
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="cleans data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input artifact str",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Output artifact str",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Output type str",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Output description str",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Min price float",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Max price float",
        required=True
    )

    args = parser.parse_args()

    go(args)
