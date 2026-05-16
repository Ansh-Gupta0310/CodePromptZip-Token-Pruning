"""
demo_viva.py - Live Demo Script for Viva

Shows the complete CodePromptZip pipeline step-by-step for a single
buggy Java code snippet:
  Step 1: Show the buggy input
  Step 2: BM25 retrieval finds the most similar solved bug
  Step 3: Neural compression shrinks the retrieved demonstration
  Step 4: Assemble the RAG prompt
  Step 5: CodeLlama generates the fix

Run from the project root:
    python demo_viva.py
    python demo_viva.py --no_codellama    (skip CodeLlama, show prompt only)
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────
DIVIDER = "=" * 65
STEP_DIV = "-" * 65
# ─────────────────────────────────────────────

def print_step(n, title):
    print(f"\n{DIVIDER}")
    print(f"  STEP {n}: {title}")
    print(DIVIDER)


def main(args):
    # ──────────────────────────────────────────────────────────────────
    # The buggy Java code we want to fix (simulates a real test query)
    # ──────────────────────────────────────────────────────────────────
    BUGGY_CODE = "public boolean isEven ( int n ) { return n % 2 = 0 ; }"
    EXPECTED_FIX = "public boolean isEven ( int n ) { return n % 2 == 0 ; }"

    # ──────────────────────────────────────────────────────────────────
    # A small in-memory "training corpus" (simulates the real 58K dataset)
    # In a real run, this comes from data/raw/bugs2fix/train.json
    # ──────────────────────────────────────────────────────────────────
    DEMO_CORPUS = [
        {
            "buggy": "public int add ( int a , int b ) { return a - b ; }",
            "fixed": "public int add ( int a , int b ) { return a + b ; }",
        },
        {
            "buggy": "public boolean check ( int x ) { if ( x = 0 ) return true ; return false ; }",
            "fixed": "public boolean check ( int x ) { if ( x == 0 ) return true ; return false ; }",
        },
        {
            "buggy": "public int max ( int a , int b ) { return a > b ? a : b ; }",
            "fixed": "public int max ( int a , int b ) { return a > b ? a : b ; }",
        },
        {
            "buggy": "public String greet ( String name ) { return \"Hello \" + name ; }",
            "fixed": "public String greet ( String name ) { return \"Hello, \" + name ; }",
        },
    ]

    # ══════════════════════════════════════════════════════════════════
    print_step(1, "THE BUGGY CODE (Test Query)")
    # ══════════════════════════════════════════════════════════════════
    print(f"\n  Input  (buggy):  {BUGGY_CODE}")
    print(f"  Target (correct): {EXPECTED_FIX}")
    print(f"\n  Bug: '= 0' should be '== 0'  (assignment used instead of equality check)")

    # ══════════════════════════════════════════════════════════════════
    print_step(2, "BM25 RETRIEVAL — Find the Most Similar Solved Bug")
    # ══════════════════════════════════════════════════════════════════
    from src.retrieval import BM25Retriever

    retriever = BM25Retriever()
    retriever.build_index(DEMO_CORPUS, task="bugs2fix")

    query_dict = {"buggy": BUGGY_CODE}
    demos = retriever.retrieve(query_dict, task="bugs2fix", top_k=1)
    best_demo = demos[0]

    print(f"\n  Query tokens:   {BUGGY_CODE.split()[:8]} ...")
    print(f"\n  Best match found:")
    print(f"    Buggy : {best_demo['buggy']}")
    print(f"    Fixed : {best_demo['fixed']}")
    print(f"\n  Why this one? BM25 found high overlap on tokens like")
    print(f"  'boolean', 'int', '=', '0', 'return' — syntactically similar.")

    # ══════════════════════════════════════════════════════════════════
    print_step(3, "NEURAL COMPRESSION — Shrink the Retrieved Demo")
    # ══════════════════════════════════════════════════════════════════
    checkpoint_dir = "./checkpoints/best_model"

    if os.path.exists(checkpoint_dir) and not args.no_compressor:
        print(f"\n  Loading compressor from: {checkpoint_dir}")
        from src.compress import CodeCompressor
        compressor = CodeCompressor(checkpoint_dir)

        tau = 0.3
        compressed_demo = compressor.compress_demonstration(best_demo, tau, "bugs2fix")
        comp_buggy = compressed_demo.get("buggy", best_demo["buggy"])
        comp_fixed = compressed_demo.get("fixed", best_demo["fixed"])

        orig_tokens = len(best_demo["buggy"].split()) + len(best_demo["fixed"].split())
        comp_tokens = len(comp_buggy.split()) + len(comp_fixed.split())
        actual_reduction = round((1 - comp_tokens / orig_tokens) * 100, 1)

        print(f"\n  tau_code = {tau}  (remove {int(tau*100)}% of tokens)")
        print(f"\n  Before compression ({orig_tokens} tokens):")
        print(f"    Buggy : {best_demo['buggy']}")
        print(f"    Fixed : {best_demo['fixed']}")
        print(f"\n  After compression ({comp_tokens} tokens, -{actual_reduction}% reduction):")
        print(f"    Buggy : {comp_buggy}")
        print(f"    Fixed : {comp_fixed}")
    else:
        # Simulate compression using the greedy algorithm directly (no checkpoint needed)
        print(f"\n  [Using Priority-Ranking simulation — checkpoint not loaded]")
        from src.priority_ranking import compress_code_with_priority

        tau = 0.3
        comp_buggy, ratio = compress_code_with_priority(best_demo["buggy"], tau, "bugs2fix")
        comp_fixed, _ = compress_code_with_priority(best_demo["fixed"], tau, "bugs2fix")
        compressed_demo = {"buggy": comp_buggy, "fixed": comp_fixed}

        orig_tokens = len(best_demo["buggy"].split()) + len(best_demo["fixed"].split())
        comp_tokens = len(comp_buggy.split()) + len(comp_fixed.split())
        actual_reduction = round((1 - comp_tokens / orig_tokens) * 100, 1)

        print(f"\n  tau_code = {tau}  (target: remove {int(tau*100)}% of tokens)")
        print(f"\n  Before ({orig_tokens} tokens):")
        print(f"    Buggy : {best_demo['buggy']}")
        print(f"    Fixed : {best_demo['fixed']}")
        print(f"\n  After ({comp_tokens} tokens, -{actual_reduction}% reduction):")
        print(f"    Buggy : {comp_buggy}")
        print(f"    Fixed : {comp_fixed}")
        print(f"\n  Key: Identifiers/symbols removed first; Signatures kept last.")

    # ══════════════════════════════════════════════════════════════════
    print_step(4, "PROMPT ASSEMBLY — Building the RAG Prompt for CodeLlama")
    # ══════════════════════════════════════════════════════════════════
    from src.retrieval import format_rag_prompt

    prompt = format_rag_prompt(query_dict, [compressed_demo], task="bugs2fix")

    print(f"\n  Final prompt sent to CodeLlama-34B:\n")
    print(STEP_DIV)
    print(prompt)
    print(STEP_DIV)
    print(f"\n  Total tokens in prompt: ~{len(prompt.split())}")
    print(f"  Context window:          8192 tokens")
    print(f"  Tokens saved by compression: {orig_tokens - comp_tokens}")

    # ══════════════════════════════════════════════════════════════════
    print_step(5, "CODELLAMA GENERATION — The Fix")
    # ══════════════════════════════════════════════════════════════════
    if args.no_codellama:
        print("\n  [--no_codellama flag set: skipping CodeLlama inference]")
        print(f"\n  Expected CodeLlama output: {EXPECTED_FIX}")
        return

    model_path = "./codellama-34b-instruct.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        print(f"\n  [Model not found at {model_path}]")
        print(f"  Expected output: {EXPECTED_FIX}")
        return

    from src.evaluate import BaseLMInference
    import yaml
    with open("./configs/config.yaml") as f:
        config = yaml.safe_load(f)

    print(f"\n  Loading CodeLlama-34B (this takes ~30 seconds)...")
    lm = BaseLMInference(config["base_lm"])

    print(f"\n  Generating fix...")
    prediction = lm.generate(prompt)

    print(f"\n  CodeLlama output:   {prediction.strip()}")
    print(f"  Expected fix:       {EXPECTED_FIX}")

    # Score it
    from src.metrics.codebleu_metric import compute_codebleu
    score = compute_codebleu([prediction.strip()], [EXPECTED_FIX])
    print(f"\n  CodeBLEU Score: {score['codebleu']:.1f}%")
    print(f"    N-gram match:    {score['ngram_match']:.1f}%")
    print(f"    Syntax match:    {score['syntax_match']:.1f}%")
    print(f"    Dataflow match:  {score['dataflow_match']:.1f}%")

    print(f"\n{DIVIDER}")
    print("  DEMO COMPLETE — Full pipeline executed successfully!")
    print(DIVIDER)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CodePromptZip Live Demo")
    parser.add_argument("--no_codellama", action="store_true",
                        help="Skip CodeLlama inference (show prompt only)")
    parser.add_argument("--no_compressor", action="store_true",
                        help="Use greedy algo instead of neural compressor checkpoint")
    args = parser.parse_args()
    main(args)
