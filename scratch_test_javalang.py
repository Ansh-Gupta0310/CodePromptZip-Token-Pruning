import javalang

code = "[BUGGY_CODE]\nint x = 0;"
try:
    tokens = list(javalang.tokenizer.tokenize(code))
    print("passed. Tokens:")
    for t in tokens:
        print(f"{type(t).__name__}: {t.value}")
except Exception as e:
    print(f"failed: {e}")
