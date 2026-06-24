# Build an ML Pipeline for Short-Term Rental Prices in NYC

An end-to-end, reusable MLflow + Weights & Biases pipeline that ingests weekly batches of NYC Airbnb listing data, cleans and validates it, trains a Random Forest price-estimation model, and exports a production-ready model artifact. The pipeline is designed to be re-run on every new data drop with a single command, with every step's parameters driven entirely by `config.yaml` (no hardcoded values) and every intermediate dataset and model tracked and versioned in W&B.

## Submission links

- **GitHub repository**: https://github.com/adebowalep/build-ml-pipeline-for-short-term-rental-prices
- **W&B project** (public): https://wandb.ai/suleimanojo3-dsti-school-of-engineering/nyc_airbnb
- **Releases**: [v1.0.0](https://github.com/adebowalep/build-ml-pipeline-for-short-term-rental-prices/releases/tag/v1.0.0), [v1.0.1](https://github.com/adebowalep/build-ml-pipeline-for-short-term-rental-prices/releases/tag/v1.0.1)

## Table of contents

- [Submission links](#submission-links)
- [Project overview](#project-overview)
- [Architecture](#architecture)
- [Pipeline flow](#pipeline-flow)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [MLflow commands](#mlflow-commands)
- [W&B commands and manual steps](#wb-commands-and-manual-steps)
- [Artifact descriptions](#artifact-descriptions)
- [Reproducibility](#reproducibility)
- [Releasing a new pipeline version](#releasing-a-new-pipeline-version)
- [Future improvements](#future-improvements)
- [License](#license)

## Project overview

A property management company renting short-term listings across NYC needs to estimate a fair nightly price for a property given the prices of comparable listings. The company receives new bulk data every week, so the model has to be retrained on the same cadence. Rather than re-running notebooks by hand, this repository implements the whole workflow — download, clean, validate, split, train, evaluate — as a single MLflow pipeline orchestrated by Hydra, with W&B providing artifact versioning, experiment tracking, and lineage.

## Architecture

```
                ┌──────────┐
                │ download │  (provided component)
                └────┬─────┘
                     │ sample.csv
                     ▼
              ┌─────────────┐
              │basic_cleaning│
              └──────┬──────┘
                     │ clean_sample.csv
                     ▼
              ┌─────────────┐
              │ data_check   │  (pytest: schema, price range,
              └──────┬──────┘   row count, geo bounds, KL drift)
                     │ clean_sample.csv (validated)
                     ▼
              ┌─────────────┐
              │ data_split   │  (provided component)
              └──────┬──────┘
            trainval_data.csv │ test_data.csv
                     ▼                │
        ┌────────────────────┐        │
        │ train_random_forest│        │
        └─────────┬──────────┘        │
                   │ random_forest_export        │
                   ▼ (manually promoted to "prod")│
        ┌────────────────────────┐                │
        │ test_regression_model  │◄───────────────┘
        │ (run explicitly, once  │
        │  a model is "prod")    │
        └────────────────────────┘
```

Every box above is an independent MLflow project (its own `conda.yml` + `MLproject`), invoked from `main.py`. Steps under `src/` are part of this repository; steps invoked via `config['main']['components_repository']` (`get_data`, `train_val_test_split`, `test_regression_model`) are pre-built, reusable components.

You can also inspect the live lineage graph for any run in W&B — see [Artifacts → Graph view](#wb-commands-and-manual-steps), and the example below:

![W&B pipeline graph](images/wandb-pipeline-graph.png)

## Pipeline flow

1. **download** — fetches the raw CSV sample (`config.etl.sample`, e.g. `sample1.csv`) and logs it to W&B as `sample.csv`.
2. **basic_cleaning** (`src/basic_cleaning`) — downloads `sample.csv:latest`, drops rows outside `[min_price, max_price]`, parses `last_review` to a real date, drops rows outside NYC's geographic bounding box, and logs the result as `clean_sample.csv`.
3. **data_check** (`src/data_check`) — runs a pytest suite against `clean_sample.csv:latest` compared to a `clean_sample.csv:reference` tag: column schema, known neighborhood names, price range, row count, geographic bounds, and a KL-divergence drift check on the neighborhood distribution.
4. **data_split** — splits `clean_sample.csv:latest` into `trainval_data.csv` and `test_data.csv` using `config.modeling.test_size` / `stratify_by`.
5. **train_random_forest** (`src/train_random_forest`) — builds a `ColumnTransformer` (ordinal/one-hot encoding, zero-imputation, a date-delta feature, and TF-IDF on the listing title) feeding a `RandomForestRegressor`, fits it on `trainval_data.csv`, logs MAE/R² and a feature-importance plot, and exports the fitted pipeline as the `random_forest_export` model artifact.
6. **(manual)** the best run's `random_forest_export` is promoted to the `prod` alias in W&B.
7. **test_regression_model** — evaluates `random_forest_export:prod` against the held-out `test_data.csv`. Not run by default; must be invoked explicitly.

## Project structure

```
.
├── main.py                      # Pipeline orchestrator (Hydra entry point)
├── config.yaml                  # All pipeline parameters (single source of truth)
├── MLproject / conda.yml        # Root MLflow project definition
├── components/                  # Pre-built, reusable steps
│   ├── get_data/
│   ├── train_val_test_split/
│   ├── test_regression_model/
│   └── wandb_utils/             # Shared W&B artifact-logging helper
├── src/                         # Steps implemented for this project
│   ├── eda/                     # EDA.ipynb + Jupyter MLproject
│   ├── basic_cleaning/          # Cleans the raw sample
│   ├── data_check/               # pytest-based data validation suite
│   └── train_random_forest/      # Feature engineering + RF training
├── cookie-mlflow-step/           # Cookiecutter template for new steps
└── images/                       # Screenshots referenced in this README
```

## Installation

Supported on Ubuntu 22.04 / 24.04 (incl. WSL) and recent macOS, with Python 3.13.

```bash
conda env create -f environment.yml
conda activate nyc_airbnb_dev
wandb login [your API key]   # get a key at https://wandb.ai/authorize
```

## Usage

Run the full pipeline (download → basic_cleaning → data_check → data_split → train_random_forest):

```bash
mlflow run .
```

Run only a subset of steps (useful during development):

```bash
mlflow run . -P steps=download,basic_cleaning
```

Override any config value from the command line via Hydra:

```bash
mlflow run . \
  -P steps=train_random_forest \
  -P hydra_options="modeling.random_forest.n_estimators=10 etl.min_price=50"
```

Run the held-out test evaluation explicitly, once a model has been promoted to `prod` (see below):

```bash
mlflow run . -P steps=test_regression_model
```

## MLflow commands

| Purpose | Command |
|---|---|
| Run entire pipeline | `mlflow run .` |
| Run a single step | `mlflow run . -P steps=<step_name>` |
| Run multiple steps | `mlflow run . -P steps=download,basic_cleaning` |
| Override config | `mlflow run . -P hydra_options="key.path=value"` |
| Open the EDA notebook | `mlflow run src/eda` |
| Run from a tagged release, on new data | `mlflow run https://github.com/<user>/build-ml-pipeline-for-short-term-rental-prices.git -v <tag> -P hydra_options="etl.sample='sample2.csv'"` |
| Hyperparameter sweep (Hydra multirun) | `mlflow run . -P steps=train_random_forest -P hydra_options="modeling.max_tfidf_features=10,15,30 modeling.random_forest.max_features=0.1,0.33,0.5,0.75,1 -m"` |

## W&B commands and manual steps

These three steps happen in the W&B web UI and can't be scripted from this repo — they're one-time/per-release human decisions (which artifact is the reference, which model is good enough to ship):

1. **Tag a reference dataset** (once, before relying on the drift test): go to the `nyc_airbnb` project → Artifacts → `clean_sample` → the `latest` version → add the alias `reference`.

   ![tagging a reference dataset](images/wandb-tag-data-test.png)

2. **Select and promote the best model**: after a hyperparameter sweep, go to the runs table, sort by ascending `mae`, open the best run's `model_export` artifact, and add the alias `prod`.

   ![selecting the best model](images/wandb_select_best.gif)

3. **Visualize lineage**: Artifacts → any `model_export` version → **Graph view** shows the full upstream/downstream dependency graph for that model.

## Artifact descriptions

| Artifact | Type | Produced by | Description |
|---|---|---|---|
| `sample.csv` | `raw_data` | `download` | Raw weekly data drop, unmodified |
| `clean_sample.csv` | `clean_sample` | `basic_cleaning` | Price/geo outliers removed, `last_review` parsed to date |
| `trainval_data.csv` | `trainval_data` | `data_split` | Training + validation split |
| `test_data.csv` | `test_data` | `data_split` | Held-out test split, untouched until final evaluation |
| `random_forest_export` | `model_export` | `train_random_forest` | Fitted sklearn `Pipeline` (preprocessing + `RandomForestRegressor`), saved via `mlflow.sklearn.save_model`, tagged `prod` once approved |

## Reproducibility

- Every parameter (price bounds, split sizes, random seed, model hyperparameters) lives in `config.yaml` — nothing is hardcoded in any step.
- `modeling.random_forest.random_state` is fixed via `random_seed`, and `train_test_split` calls are seeded consistently, so re-running the pipeline on the same data and config reproduces the same splits and (modulo RF's internal randomness sources controlled by `random_state`) the same model.
- Every artifact consumed by a step is referenced with an explicit version or alias (`:latest`, `:reference`, `:prod`) so a given pipeline run's full data lineage is reconstructable from W&B alone.
- Each step ships its own `conda.yml` with pinned dependency versions, so steps run in isolated, reproducible environments regardless of what's installed on the host machine.

## Releasing a new pipeline version

1. Copy the best hyperparameters found during the sweep into `config.yaml` so they become the new defaults.
2. Commit, push, and cut a GitHub release (e.g. `1.0.0`):

   ![tagging a GitHub release](images/tag-release-github.png)

3. To retrain on a new data sample without touching the repo locally:

   ```bash
   mlflow run https://github.com/adebowalep/build-ml-pipeline-for-short-term-rental-prices.git \
     -v v1.0.0 \
     -P hydra_options="etl.sample='sample2.csv'"
   ```

   **Verified result on `v1.0.0` against `sample2.csv`:** the full pipeline (download → basic_cleaning → data_check → data_split → train_random_forest) ran end-to-end successfully — all 6 `data_check` tests passed (`test_column_names`, `test_neighborhood_names`, `test_proper_boundaries`, `test_similar_neigh_distrib`, `test_row_count`, `test_price_range`), and training completed with MAE ≈ 32.4.

   This is the expected outcome for this implementation: unlike a bare-minimum implementation, `basic_cleaning` here filters rows outside NYC's geographic bounding box (see `NYC_LONGITUDE_RANGE` / `NYC_LATITUDE_RANGE` in `src/basic_cleaning/run.py`) as part of the original `v1.0.0` design, not as a later patch. The geographic-outlier failure mode that a bare-minimum implementation would hit on `sample2.csv` is therefore handled proactively and never reaches `data_check`. If a future data sample exposes a *different* validation failure (e.g. a new neighborhood group, a price-range violation, or a distribution shift the KL-divergence test catches), it should be fixed in the relevant step, committed, and released as the next patch version (`1.0.1`, etc.), following the same release process above.

## Future improvements

- Replace the single train/validation split with k-fold cross-validation for a more stable MAE estimate, especially useful since the sweep currently selects hyperparameters off a single validation split.
- Add automated drift monitoring (the KL-divergence check currently only runs as part of `data_check`) as a standing, scheduled job independent of training runs, so distribution shifts are caught even between retraining cycles.
- Explore gradient-boosted tree models (LightGBM/XGBoost) as a stronger baseline than Random Forest, and add a model-comparison step that only promotes a challenger if it beats the current `prod` model's MAE on the test set.
- Add richer geospatial features (distance to subway, neighborhood-level median price) instead of relying solely on raw `latitude`/`longitude`.
- Wrap `test_regression_model`'s pass/fail decision into a CI gate so a regression in test-set MAE blocks a release rather than relying on a human to check W&B before promoting `prod`.
- Add a `conftest.py`-level fixture cache or smaller sample fixtures so `data_check` doesn't need a full W&B round-trip during local development/CI.

## License

[License](LICENSE.txt)
