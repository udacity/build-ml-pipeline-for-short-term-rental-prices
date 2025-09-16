from setuptools import setup


setup(
    name="wandb-utils",
    version="0.1",
    description="Utilities for interacting with Weights and Biases and mlflow",
    zip_safe=False,  # avoid eggs, which make the handling of package data cumbersome
    packages=["wandb_utils"],
    python_requires='>=3.13',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "mlflow",
        "wandb"
    ]
)
