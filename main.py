import json

import mlflow
import tempfile
import os
import wandb
import hydra
from omegaconf import DictConfig

_steps = [
    "download",
    "basic_cleaning",
    "data_check",
    "data_split",
    "train_random_forest",
    # NOTE: We do not include this in the steps so it is not run by mistake.
    # You first need to promote a model export to "prod" before you can run this,
    # then you need to run this step explicitly
#    "test_regression_model"
]


# This automatically reads in the configuration
@hydra.main(version_base=None, config_name='config', config_path='.')  # Adding version_base for Python 3.13 compatibility
def go(config: DictConfig):

    # Setup the wandb experiment. All runs will be grouped under this name
    os.environ["WANDB_PROJECT"] = config["main"]["project_name"]
    os.environ["WANDB_RUN_GROUP"] = config["main"]["experiment_name"]

    # Steps to execute
    steps_par = config['main']['steps']
    active_steps = steps_par.split(",") if steps_par != "all" else _steps

    # Move to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        if "download" in active_steps:
            # Download file and load in W&B
            _ = mlflow.run(
                f"{config['main']['components_repository']}/get_data",
                "main",
                env_manager="conda",
                parameters={
                    "sample": config["etl"]["sample"],
                    "artifact_name": "sample.csv",
                    "artifact_type": "raw_data",
                    "artifact_description": "Raw file as downloaded"
                },
            )

        if "basic_cleaning" in active_steps:
            _ = mlflow.run(
                os.path.join(hydra.utils.get_origina_cwd(), "src", "basic_cleaning"),
                "main",
                env_manager="conda",
                parameters={
                    "input_artifact": "idris-isah2-udacity/nyc_airbnb/sample.csv:latest",
                    "output_artifact": "clean_sample.csv",
                    "output_type": "clean_sample",
                    "output_description": "Data with outliers and null values removed",
                    "min_price": config['etl']['min_price'],
                    "max_price": config['etl']['max_price']
                },
            )

        if "data_check" in active_steps:
            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "data_check"),
                "main",
                env_manager="conda",
                parameters={
                    "csv": "idris-isah2-udacity/nyc_airbnb/sample.csv:latest",
                    "ref": "idris-isah2-udacity/nyc_airbnb/cleaned_sample.csv:reference",
                    "kl_threshold": config['data_check']['kl_threshold'],
                    "min_price": config['etl']['min_price'],
                    "max_price": config['etl']['max_price']
                },
            )


        if "data_split" in active_steps:
            _ = mlflow.run(
                f"{config['main']['components_repository']}/train_val_test_split",
                "main",
                env_manager="conda",
                parameters={
                    "input": "idris-isah2-udacity/nyc_airbnb/clean_sample.csv:reference",
                    "test_size": config['modeling']['test_size'],
                    "random_seed": config['modeling']['test_size'],
                    "stratify_by": config['modeling']['stratify_by']
                },
            )

        if "train_random_forest" in active_steps:

            rf_config = os.path.abspath("rf_config.json")
            with open(rf_config, "w+") as fp:
                json.dump(dict(config["modeling"]["random_forest"].items()), fp)

            _ = mlflow.run(
                os.path.join(hydra.utils.get_original_cwd(), "src", "train_random_forest"),
                "main",
                env_manager="conda",
                parameters={
                    "trainval_artifact": "idris-isah2-udacity/nyc_airbnb/trainval_data.csv:latest",
                    "val_size": config['modeling']['val_size'],
                    "random_seed": config['modeling']['random_seed'],
                    "stratify_by": config['modeling']['stratify_by'],
                    "rf_config": rf_config,
                    "max_tfidf_features": config['modeling']['max_tfidf_features'],
                    "output_artifact": "random_forest_export"
                },
            )

        if "test_regression_model" in active_steps:

            ##################
            # Implement here #
            ##################

            pass


if __name__ == "__main__":
    go()
