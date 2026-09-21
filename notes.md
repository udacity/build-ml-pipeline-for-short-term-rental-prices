# EDA checklist

Use this checklist while working in `EDA.ipynb`. It records the required observations without implementing the analysis for you.

- Fetch the `sample.csv:latest` artifact from the `nyc_airbnb` W&B project and load it into a dataframe.
- Add Markdown cells that explain each exploration and cleaning decision.
- Inspect missing values. Record that they are not imputed during this EDA because the inference pipeline must handle them later.
- Treat the accepted nightly price range as inclusive: `$10 <= price <= $350`.
- Convert `last_review` from text to a datetime value.
- Re-run the profile or equivalent dataframe inspection after your changes.
- Finish the W&B run.
- Restart the notebook kernel, run all cells from top to bottom, and resolve any errors.
- Save the completed notebook as `EDA.ipynb` in the repository root.
