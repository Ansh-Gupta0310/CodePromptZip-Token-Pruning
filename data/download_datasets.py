"""
download_datasets.py - Download datasets for CodePromptZip experiments

Downloads:
1. Bugs2Fix (CodeXGLUE code refinement - medium) from HuggingFace
2. (Future) Assertion Generation dataset
3. (Future) Code Suggestion dataset
"""

import os
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from datasets import load_dataset
from tqdm import tqdm


def download_bugs2fix(output_dir: str):
    """
    Download the Bugs2Fix (medium) dataset from CodeXGLUE.
    Medium subset: code snippets with 50-100 tokens.

    The paper uses this dataset with stats:
        Train: 52,364 | Test: 6,545 | Val: 6,546
    """
    print("=" * 60)
    print("Downloading Bugs2Fix (CodeXGLUE Code Refinement - medium)")
    print("=" * 60)

    output_path = Path(output_dir) / "bugs2fix"
    output_path.mkdir(parents=True, exist_ok=True)

    # Load from HuggingFace
    dataset = load_dataset("code_x_glue_cc_code_refinement", "medium")

    for split_name in ["train", "validation", "test"]:
        split_data = dataset[split_name]
        samples = []

        for item in tqdm(split_data, desc=f"Processing {split_name}"):
            samples.append({
                "buggy": item["buggy"],
                "fixed": item["fixed"],
            })

        # Save to JSON
        out_file = output_path / f"{split_name}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(samples, f, indent=2, ensure_ascii=False)

        print(f"  {split_name}: {len(samples)} samples -> {out_file}")

    print(f"\nBugs2Fix download complete! Saved to {output_path}\n")


def download_assertion_generation(output_dir: str):
    """
    Download/prepare the Assertion Generation dataset.
    Based on Nashid et al. (ICSE 2023) / ATLAS dataset.

    NOTE: This dataset needs to be obtained from the paper's replication package
    or the ATLAS repository. This function creates a placeholder structure.
    """
    print("=" * 60)
    print("Assertion Generation Dataset")
    print("=" * 60)

    output_path = Path(output_dir) / "assertion"
    output_path.mkdir(parents=True, exist_ok=True)

    # Create placeholder instructions
    readme = output_path / "README.md"
    readme.write_text(
        "# Assertion Generation Dataset\n\n"
        "## How to obtain:\n"
        "1. Download from the CodePromptZip replication package:\n"
        "   https://anonymous.4open.science/r/CodePromptZip-6B2B\n\n"
        "2. Or from the ATLAS paper repository:\n"
        "   https://github.com/mernst/ATLAS\n\n"
        "## Expected format:\n"
        "Each sample should have:\n"
        "- `focal_method`: The method under test\n"
        "- `test_method`: The partial unit test\n"
        "- `assertion`: The assertion statement (target)\n\n"
        "## Expected files:\n"
        "- train.json (144,112 samples)\n"
        "- validation.json (18,816 samples)\n"
        "- test.json (18,027 samples)\n"
    )

    print(f"  Placeholder created at {output_path}")
    print("  Please download the dataset manually (see README.md)")
    print()


def download_code_suggestion(output_dir: str):
    """
    Download/prepare the Code Suggestion dataset.
    Based on Chen et al. (ICSE 2024).

    NOTE: This dataset needs to be obtained from:
    https://github.com/iCSawyer/CodeSuggestion
    """
    print("=" * 60)
    print("Code Suggestion Dataset")
    print("=" * 60)

    output_path = Path(output_dir) / "suggestion"
    output_path.mkdir(parents=True, exist_ok=True)

    # Create placeholder instructions
    readme = output_path / "README.md"
    readme.write_text(
        "# Code Suggestion Dataset\n\n"
        "## How to obtain:\n"
        "1. Download from the CodePromptZip replication package:\n"
        "   https://anonymous.4open.science/r/CodePromptZip-6B2B\n\n"
        "2. Or from the Code Suggestion paper repository:\n"
        "   https://github.com/iCSawyer/CodeSuggestion\n\n"
        "## Expected format:\n"
        "Each sample should have:\n"
        "- `method_header`: Summary of the function\n"
        "- `method_body`: The full method body (target)\n\n"
        "## Expected files:\n"
        "- train.json (128,724 samples)\n"
        "- validation.json (5,149 samples)\n"
        "- test.json (10,727 samples)\n"
    )

    print(f"  Placeholder created at {output_path}")
    print("  Please download the dataset manually (see README.md)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Download datasets for CodePromptZip")
    parser.add_argument("--output_dir", type=str, default="./data/raw",
                        help="Output directory for raw datasets")
    parser.add_argument("--task", type=str, default="all",
                        choices=["all", "bugs2fix", "assertion", "suggestion"],
                        help="Which dataset to download")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.task in ["all", "bugs2fix"]:
        download_bugs2fix(args.output_dir)

    if args.task in ["all", "assertion"]:
        download_assertion_generation(args.output_dir)

    if args.task in ["all", "suggestion"]:
        download_code_suggestion(args.output_dir)

    print("=" * 60)
    print("Dataset download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
