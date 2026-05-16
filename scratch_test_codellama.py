import os
import sys

from src.evaluate import BaseLMInference

def test_codellama():
    prompt = """Demonstrations:
[START]
[BUGGY_CODE]:
public int add ( int a , int b ) { return a - b ; }

[FIXED_CODE]:
public int add ( int a , int b ) { return a + b ; }

...
[END]
Query:
[START]
[BUGGY_CODE]:
public void bar ( ) { int y = 0 ; if ( y = 2 ) { } }

[FIXED_CODE]:"""


    print("--- TESTING REAL CODELLAMA (34B) ---")
    model_path = "./codellama-34b-instruct.Q4_K_M.gguf"
    if os.path.exists(model_path):
        print("Loading real CodeLlama model (this takes a moment)...")
        # 4090 Optimized settings from config.yaml
        real_config = {
            "model_path": model_path, 
            "dummy_mode": False,
            "n_ctx": 8192,
            "n_gpu_layers": 128
        }
        real_lm = BaseLMInference(real_config)
        real_output = real_lm.generate(prompt)
        print(f"Real Output:\n{real_output}")
    else:
        print(f"Cannot run real test: Model not found at {model_path}")
        print("You must download the CodeLlama 34B .gguf file to run the real AI!")

if __name__ == "__main__":
    test_codellama()

