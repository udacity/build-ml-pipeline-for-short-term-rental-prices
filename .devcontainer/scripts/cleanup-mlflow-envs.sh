#!/bin/bash
# Cleanup all MLflow-created conda environments

set -e

echo "🧹 Cleaning up MLflow conda environments..."

# List all mlflow environments
ENVS=$(conda info --envs | grep mlflow | cut -f1 -d" ")

if [ -z "$ENVS" ]; then
    echo "✅ No MLflow environments to clean up"
    exit 0
fi

echo "Found environments:"
echo "$ENVS"
echo ""

read -p "Remove all these environments? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for env in $ENVS; do
        echo "Removing $env..."
        conda remove --name $env --all -y
    done
    echo "✅ Cleanup complete!"
else
    echo "❌ Cleanup cancelled"
fi
