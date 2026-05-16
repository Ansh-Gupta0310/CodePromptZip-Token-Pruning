import os
import torch
import warnings

# Suppress some HuggingFace warnings for clean output
warnings.filterwarnings("ignore")

from src.compress import CodeCompressor

def test_compressor():
    # Make sure we have the checkpoint
    checkpoint = "./checkpoints/best_model"
    if not os.path.exists(checkpoint):
        print(f"Error: Could not find model checkpoint at {checkpoint}")
        return

    print("Loading model...")
    compressor = CodeCompressor(checkpoint, device="cuda" if torch.cuda.is_available() else "cpu")

    demo = {
        "buggy": "public int add(int a, int b) {\n    int sum = a - b;\n    return sum;\n}",
        "fixed": "public int add(int a, int b) {\n    int sum = a + b;\n    return sum;\n}"
    }

    print("\n--- ORIGINAL DEMO ---")
    print(f"Buggy: {demo['buggy']}")
    print(f"Fixed: {demo['fixed']}")

    print("\n--- COMPRESSING (tau=0.5) ---")
    # Compress the dictionary!
    compressed_demo = compressor.compress_demonstration(demo, tau_code=0.5, task="bugs2fix")

    print("\n--- COMPRESSED DEMO ---")
    print(f"Buggy: {compressed_demo.get('buggy', '')}")
    print(f"Fixed: {compressed_demo.get('fixed', '')}")

if __name__ == "__main__":
    test_compressor()
