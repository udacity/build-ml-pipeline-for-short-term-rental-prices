#!/bin/bash
set -e

echo "🔧 Running on-create setup..."

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate nyc_airbnb_dev

# Install the wandb_utils package in editable mode
echo "📦 Installing wandb_utils package..."
cd /workspaces/build-ml-pipeline-for-short-term-rental-prices/components
pip install -e .

# Create necessary directories
echo "📁 Creating working directories..."
cd /workspaces/build-ml-pipeline-for-short-term-rental-prices
mkdir -p data
mkdir -p mlruns
mkdir -p outputs

# Pre-download sample data to speed up first run
echo "📥 Pre-downloading sample data..."
if [ ! -f "data/sample1.csv" ]; then
    echo "Sample data not found - will be downloaded on first run"
fi

echo "✅ On-create setup complete!"
