#!/bin/bash
set -e

echo "🚀 Running post-create setup..."

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate nyc_airbnb_dev

# Verify installations
echo "🔍 Verifying installations..."
python --version
conda --version
mlflow --version
pip list | grep wandb

# Check for WANDB_API_KEY
if [ -z "$WANDB_API_KEY" ]; then
    echo "⚠️  WARNING: WANDB_API_KEY is not set!"
    echo "📝 Please add your W&B API key:"
    echo "   1. Go to https://wandb.ai/authorize"
    echo "   2. Copy your NEW v1 API key (format: wandb_v1_...)"
    echo "   3. Add it to GitHub Codespaces secrets"
    echo "   4. Rebuild this codespace"
else
    echo "✅ WANDB_API_KEY is set"
    # Verify key format
    if [[ $WANDB_API_KEY == wandb_v1_* ]]; then
        echo "✅ Using v1 API key format (secure)"
    else
        echo "⚠️  Legacy API key detected. Consider upgrading to v1 format."
    fi
    # Configure wandb
    wandb login --relogin <<< "$WANDB_API_KEY"
fi

echo "✅ Post-create setup complete!"
