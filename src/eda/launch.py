#!/usr/bin/env python
"""Launch JupyterLab with the repository root as its workspace."""

import os
from pathlib import Path


def main():
    repository_root = Path(__file__).resolve().parents[2]
    os.chdir(repository_root)
    os.execvp(
        "jupyter-lab",
        ["jupyter-lab", f"--ServerApp.root_dir={repository_root}"],
    )


if __name__ == "__main__":
    main()
