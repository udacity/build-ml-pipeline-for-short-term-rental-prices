#!/bin/bash
set -e

echo "🔧 Running post-create setup..."

source /opt/conda/etc/profile.d/conda.sh

# Initialize conda for the vscode user (idempotent - safe to run multiple times)
echo ""
echo "🔧 Initializing conda for user shells..."
if ! grep -q "conda initialize" ~/.bashrc 2>/dev/null; then
    /opt/conda/bin/conda init bash
    echo "✓ Conda initialized for bash"
else
    echo "✓ Conda already initialized for bash"
fi

if ! grep -q "conda initialize" ~/.zshrc 2>/dev/null; then
    /opt/conda/bin/conda init zsh
    echo "✓ Conda initialized for zsh"
else
    echo "✓ Conda already initialized for zsh"
fi

conda activate nyc_airbnb_dev

# Verify installations
python --version
mlflow --version
wandb --version

# Handle W&B authentication
if [ -z "$WANDB_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: WANDB_API_KEY is not set!"
    echo ""
    echo "To complete setup:"
    echo "  1. Go to https://wandb.ai/authorize"
    echo "  2. Copy your NEW v1 API key (format: wandb_v1_...)"
    echo "  3. GitHub Settings → Codespaces → Secrets → New secret"
    echo "     Name: WANDB_API_KEY"
    echo "     Value: [your key]"
    echo "  4. Rebuild container (Cmd+Shift+P → 'Rebuild Container')"
    echo ""
    echo "📝 NOTE: v1 API keys are longer (86 chars) and more secure."
    echo ""
else
    echo "✓ WANDB_API_KEY found"
    # Verify key format
    if [[ $WANDB_API_KEY == wandb_v1_* ]]; then
        echo "✓ Using v1 API key format (secure)"
    else
        echo "⚠️  Legacy API key detected. Consider upgrading to v1 format."
    fi
    wandb login --relogin <<< "$WANDB_API_KEY"
    echo "✓ W&B login successful!"
fi

# Configure persistent conda auto-activation (runs AFTER Oh My Zsh setup)
echo ""
echo "🔧 Configuring shell auto-activation..."

# Configure for zsh (default terminal)
if [ -f ~/.zshrc ]; then
    # Check if already configured (avoid duplicates on rebuilds)
    if ! grep -q "conda activate nyc_airbnb_dev" ~/.zshrc; then
        echo "" >> ~/.zshrc
        echo "# Auto-activate nyc_airbnb_dev conda environment" >> ~/.zshrc
        echo "conda activate nyc_airbnb_dev 2>/dev/null || true" >> ~/.zshrc
        echo "" >> ~/.zshrc
        echo "# Welcome message (only show for interactive shells)" >> ~/.zshrc
        echo 'if [[ $- == *i* ]] && [[ -z "$CODESPACE_WELCOME_SHOWN" ]]; then' >> ~/.zshrc
        echo '  export CODESPACE_WELCOME_SHOWN=1' >> ~/.zshrc
        echo '  echo ""' >> ~/.zshrc
        echo '  echo "=========================================="' >> ~/.zshrc
        echo '  echo "  ML Workflow Exercises - Codespace"' >> ~/.zshrc
        echo '  echo "=========================================="' >> ~/.zshrc
        echo '  echo ""' >> ~/.zshrc
        echo '  echo "Environment: Python $(python --version 2>&1 | cut -d\" \" -f2), MLflow $(mlflow --version 2>&1 | awk '\''{print $NF}'\'')"' >> ~/.zshrc
        echo '  echo "Disk Space: $(df -h /workspaces 2>/dev/null | tail -1 | awk '\''{print $4}'\'') available"' >> ~/.zshrc
        echo '  echo ""' >> ~/.zshrc
        echo '  echo "Quick Start:"' >> ~/.zshrc
        echo '  echo "  cd lesson-X-*/exercises/exercise_Y/solution"' >> ~/.zshrc
        echo '  echo "  conda env create -f conda.yml"' >> ~/.zshrc
        echo '  echo "  conda activate <env_name>"' >> ~/.zshrc
        echo '  echo "  mlflow run ."' >> ~/.zshrc
        echo '  echo ""' >> ~/.zshrc
        echo '  echo "Docs: README.md | CODESPACES_QUICKSTART.md"' >> ~/.zshrc
        echo '  echo ""' >> ~/.zshrc
        echo 'fi' >> ~/.zshrc
        echo "✓ Zsh auto-activation configured"
    else
        echo "✓ Zsh auto-activation already configured"
    fi

# Configure for bash (fallback)
elif [ -f ~/.bashrc ]; then
    if ! grep -q "conda activate nyc_airbnb_dev" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# Auto-activate nyc_airbnb_dev conda environment" >> ~/.bashrc
        echo "conda activate nyc_airbnb_dev 2>/dev/null || true" >> ~/.bashrc
        echo "" >> ~/.bashrc
        echo "# Welcome message (only show for interactive shells)" >> ~/.bashrc
        echo 'if [[ $- == *i* ]] && [[ -z "$CODESPACE_WELCOME_SHOWN" ]]; then' >> ~/.bashrc
        echo '  export CODESPACE_WELCOME_SHOWN=1' >> ~/.bashrc
        echo '  echo ""' >> ~/.bashrc
        echo '  echo "=========================================="' >> ~/.bashrc
        echo '  echo "  ML Workflow Exercises - Codespace"' >> ~/.bashrc
        echo '  echo "=========================================="' >> ~/.bashrc
        echo '  echo ""' >> ~/.bashrc
        echo '  echo "Environment: Python $(python --version 2>&1 | cut -d\" \" -f2), MLflow $(mlflow --version 2>&1 | awk '\''{print $NF}'\'')"' >> ~/.bashrc
        echo '  echo "Disk Space: $(df -h /workspaces 2>/dev/null | tail -1 | awk '\''{print $4}'\'') available"' >> ~/.bashrc
        echo '  echo ""' >> ~/.bashrc
        echo '  echo "Quick Start:"' >> ~/.bashrc
        echo '  echo "  cd lesson-X-*/exercises/exercise_Y/solution"' >> ~/.bashrc
        echo '  echo "  conda env create -f conda.yml"' >> ~/.bashrc
        echo '  echo "  conda activate <env_name>"' >> ~/.bashrc
        echo '  echo "  mlflow run ."' >> ~/.bashrc
        echo '  echo ""' >> ~/.bashrc
        echo '  echo "Docs: README.md | CODESPACES_QUICKSTART.md"' >> ~/.bashrc
        echo '  echo ""' >> ~/.bashrc
        echo 'fi' >> ~/.bashrc
        echo "✓ Bash auto-activation configured"
    else
        echo "✓ Bash auto-activation already configured"
    fi
fi

echo "✓ Shell configuration complete!"
