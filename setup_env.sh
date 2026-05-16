#!/bin/bash
# CodePromptZip Environment Setup Script for Linux
# Run: bash setup_env.sh
#
# Explicitly uses Python 3.12 to ensure full compatibility with
# all ML dependencies (PyTorch CUDA, tree-sitter, llama-cpp-python).

set -e  # Exit immediately on any error

REQUIRED_PYTHON="python3.12"

echo -e "\e[36m=== CodePromptZip Environment Setup ===\e[0m"

# ──────────────────────────────────────────────────────────────
# 0. Ensure Python 3.12 is installed
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[0/5] Checking for Python 3.12...\e[0m"

if ! command -v $REQUIRED_PYTHON &> /dev/null; then
    echo -e "\e[33m  Python 3.12 not found. Installing via deadsnakes PPA...\e[0m"
    sudo apt-get update -qq
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update -qq
    sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
    echo -e "\e[32m  Python 3.12 installed successfully.\e[0m"
else
    PY_VER=$($REQUIRED_PYTHON --version 2>&1)
    echo -e "\e[32m  Found: $PY_VER\e[0m"
fi

# ──────────────────────────────────────────────────────────────
# 1. Create virtual environment explicitly with python3.12
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[1/5] Creating Python 3.12 virtual environment...\e[0m"
$REQUIRED_PYTHON -m venv venv
echo -e "\e[32m  -> Virtual environment created at ./venv (Python 3.12)\e[0m"

# Use the venv's own python/pip from now on
VENV_PYTHON="./venv/bin/python"
VENV_PIP="./venv/bin/pip"

# Confirm the venv is actually 3.12
VENV_VER=$($VENV_PYTHON --version 2>&1)
echo -e "\e[32m  -> venv Python: $VENV_VER\e[0m"

# ──────────────────────────────────────────────────────────────
# 2. Upgrade pip
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[2/5] Upgrading pip...\e[0m"
$VENV_PYTHON -m pip install --upgrade pip

# ──────────────────────────────────────────────────────────────
# 3. Install requirements
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[3/5] Installing project requirements...\e[0m"
$VENV_PIP install -r requirements.txt

# ──────────────────────────────────────────────────────────────
# 4. Verify installation
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[4/5] Verifying installation...\e[0m"
echo -e "\e[36m=== Verification ===\e[0m"

$VENV_PYTHON -c "
import sys
print(f'Python:       {sys.version}')
"

$VENV_PYTHON -c "
import torch
print(f'PyTorch:      {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU:          {torch.cuda.get_device_name(0)}')
    print(f'VRAM:         {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB')
else:
    print('GPU:          None (check CUDA drivers)')
"

$VENV_PYTHON -c "import transformers; print(f'Transformers: {transformers.__version__}')"
$VENV_PYTHON -c "import javalang; print('javalang:     OK')"
$VENV_PYTHON -c "import rank_bm25; print('rank_bm25:    OK')"
$VENV_PYTHON -c "from codebleu import calc_codebleu; print('codebleu:     OK')"

# ──────────────────────────────────────────────────────────────
# 5. Create required project directories
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[33m[5/5] Creating project directories...\e[0m"
for d in "data/raw" "data/processed" "data/compression_dataset" "results" "checkpoints" "logs"; do
    mkdir -p "$d"
    echo -e "\e[32m  Created: $d\e[0m"
done

# ──────────────────────────────────────────────────────────────
# Done
# ──────────────────────────────────────────────────────────────
echo -e "\n\e[36m=== Setup Complete! ===\e[0m"
echo -e "\e[33mActivate the environment:\e[0m  source venv/bin/activate"
echo -e "\e[33mVerify GPU training works:\e[0m python scripts/run_quick_test.py"
echo -e "\e[33mStart training:\e[0m            python src/train.py --config configs/config.yaml"
