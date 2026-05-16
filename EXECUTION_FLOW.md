<p align="center">
  <img src="https://img.shields.io/badge/🚀-Execution_Flow-blueviolet?style=for-the-badge&labelColor=1a1a2e" alt="Execution Flow" height="40"/>
</p>

> **Complete step-by-step guide** to reproduce the full CodePromptZip pipeline from scratch on a Linux system with an NVIDIA GPU.

---

## 🛠️ Prerequisites

| Requirement | Specification |
| :--- | :--- |
| 🐧 **OS** | Linux (Ubuntu 20.04+ recommended) |
| 🖥️ **GPU** | NVIDIA GPU with ≥24 GB VRAM (e.g., RTX 4090) |
| 🧮 **CUDA** | 12.1+ with compatible drivers |
| 🐍 **Python** | 3.12 |
| 💾 **Disk Space** | ~40 GB (dataset + model weights + checkpoints) |

---

## ⚡ Phase 0 — Environment Setup

```bash
# Make the setup script executable and run it
chmod +x setup_env.sh
bash setup_env.sh

# Activate the virtual environment
source venv/bin/activate
```

<details>
<summary><strong>What does <code>setup_env.sh</code> do?</strong></summary>

1. Checks for / installs Python 3.12 via the deadsnakes PPA
2. Creates a virtual environment (`./venv`)
3. Installs all dependencies from `requirements.txt` (PyTorch, Transformers, llama-cpp-python, etc.)
4. Creates required project directories (`data/`, `results/`, `checkpoints/`, `logs/`)
5. Verifies the installation (CUDA, GPU detection)

</details>

### 📥 Download the CodeLlama Model (for evaluation)

Download the quantized CodeLlama-34B-Instruct GGUF model (~20 GB) and place it in the project root:

```bash
# Example using wget (replace URL with your source)
wget -O codellama-34b-instruct.Q4_K_M.gguf <YOUR_DOWNLOAD_URL>
```

---

## 📊 Phase 1 — Data Preparation

### Step 1.1: Download the Bugs2Fix Dataset

```bash
python data/download_datasets.py --task bugs2fix
```

- **Output:** `data/raw/bugs2fix/{train,validation,test}.json`
- **Stats:** 52,364 train · 6,546 validation · 6,545 test buggy–fixed Java code pairs (CodeXGLUE medium subset)

### Step 1.2: Construct the Compression Dataset

```bash
python src/dataset_construction.py --config configs/config.yaml
```

<details>
<summary><strong>What it does</strong></summary>

1. Parses each code example into an AST using JavaParser
2. Categorizes every token into one of 5 types (Identifier, Invocation, Structure, Symbol, Signature)
3. Applies the priority-driven greedy removal algorithm at 9 compression ratios (τ = 0.1 to 0.9)
4. Splits at the example level (80/10/10) to prevent data leakage

</details>

- **Output:** `data/compression_dataset/{train,val,test}.json`
- **Stats:** 52,364 × 9 = **471,276** compression triples → 377,020 train · 47,128 val · 47,128 test

---

## 🧠 Phase 2 — Training

### Step 2.1: Train the Copy-Enhanced CodeT5 Compressor

```bash
python src/train.py --config configs/config.yaml
```

**Key training settings** (from `configs/config.yaml`):

| Setting | Value |
| :--- | :--- |
| Base Model | `Salesforce/codet5-large` (770M params) |
| Effective Batch Size | 32 (micro-batch 8 × accumulation 4) |
| Learning Rate | 5 × 10⁻⁵ |
| Epochs | 10 |
| Mixed Precision | FP16 |
| Gradient Checkpointing | ✅ Enabled |

- **Output:** Best model checkpoint → `checkpoints/best_model/`
- **Logs:** Training logs → `logs/`

> 📈 **Monitoring:** Use TensorBoard to track training and validation loss:
> ```bash
> tensorboard --logdir ./logs
> ```

---

## 🧪 Phase 3 — Evaluation

### Step 3.1: Run the Full Evaluation Suite

```bash
python scripts/run_all_evaluations.py \
    --config configs/config.yaml \
    --checkpoint ./checkpoints/best_model \
    --max_eval_samples 2000
```

**What it runs** (13 experiments total):

| Group | Experiments | Description |
| :--- | :--- | :--- |
| 📉 **Compression Ratio Sweep** | τ = {0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9} × 1-shot | Impact of compression level |
| 🎯 **Multi-Shot Ablation** | shots = {0, 2, 3} × τ = 0.3 | Impact of number of demonstrations |
| 📏 **Uncompressed Baselines** | shots = {1, 2, 3} × τ = 0.0 | Isolation of compression vs. retrieval |

<details>
<summary><strong>Pipeline per experiment</strong></summary>

1. Build BM25 index on 52,364 training examples
2. Retrieve top-k demonstrations for each test query
3. Compress demonstrations using the trained CodeT5 compressor (on GPU)
4. Free GPU → load CodeLlama-34B-Instruct (sequential two-phase GPU swap)
5. Generate fixes using the RAG prompt
6. Compute CodeBLEU metrics

</details>

- **Output:** Individual JSON results in `results/` and a consolidated summary in `results/all_results_summary.json`

> 🔄 **Resuming after interruption:**
> ```bash
> python scripts/run_all_evaluations.py \
>     --config configs/config.yaml \
>     --checkpoint ./checkpoints/best_model \
>     --max_eval_samples 2000 \
>     --skip_existing
> ```

### Step 3.2: Run a Single Evaluation (optional)

```bash
python src/evaluate.py \
    --config configs/config.yaml \
    --checkpoint ./checkpoints/best_model \
    --tau_code 0.3 \
    --num_shots 1 \
    --max_eval_samples 100
```

---

## 📈 Phase 4 — Visualization & Demo

### Step 4.1: Generate Result Plots

```bash
python scripts/plot_results.py
```

**Output plots** (saved to `results/plots/`):
- 📉 `plot_compression_ratio_sweep.png` — CodeBLEU vs. compression ratio
- 📉 `plot_token_savings.png` — Token reduction at each τ
- 📊 `plot_num_shots_comparison.png` — Multi-shot comparison (with/without compression)
- 📊 `plot_ablation_summary.png` — Combined ablation summary
- 📉 `plot_training_curve.png` — Training/validation loss curve
- 📄 `results_table.md` — LaTeX-ready results table

### Step 4.2: Run the Interactive Demo

```bash
# Full pipeline demo with CodeLlama generation
python demo_viva.py

# Quick demo (skip CodeLlama, verify retrieval + compression only)
python demo_viva.py --no_codellama

# Demo using the greedy algorithm instead of neural compressor
python demo_viva.py --no_compressor
```

**Demo steps:**
1. **Show** the buggy Java input
2. **Retrieve** the most similar solved bug via BM25
3. **Compress** the retrieved demonstration using the trained compressor
4. **Assemble** the RAG prompt
5. **Generate** the fix using CodeLlama-34B

---

## 📋 Quick Reference — All Commands

```bash
# ── Setup ──────────────────────────────────────────────
bash setup_env.sh
source venv/bin/activate

# ── Data ───────────────────────────────────────────────
python data/download_datasets.py --task bugs2fix
python src/dataset_construction.py --config configs/config.yaml

# ── Train ──────────────────────────────────────────────
python src/train.py --config configs/config.yaml

# ── Evaluate ───────────────────────────────────────────
python scripts/run_all_evaluations.py --config configs/config.yaml --checkpoint ./checkpoints/best_model --max_eval_samples 2000

# ── Plot ───────────────────────────────────────────────
python scripts/plot_results.py

# ── Demo ───────────────────────────────────────────────
python demo_viva.py
```
