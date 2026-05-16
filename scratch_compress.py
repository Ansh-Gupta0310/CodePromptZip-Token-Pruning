import sys
import os

sys.path.append(os.path.abspath('.'))
from src.dataset_construction import DatasetBuilder

builder = DatasetBuilder("configs/config.yaml")

example = """[BUGGY_CODE]
public static TYPE_1 init(java.lang.String name, java.util.Date date) {
    TYPE_1 VAR_1 = new TYPE_1();
    VAR_1.METHOD_1(name);
    java.util.Calendar VAR_2 = java.util.Calendar.getInstance();
    VAR_2.METHOD_2(date);
    VAR_1.METHOD_3(VAR_2);
    return VAR_1;
}
[FIXED_CODE]
public static TYPE_1 init(java.lang.String name, java.util.Date date) {
    TYPE_1 VAR_1 = new TYPE_1();
    VAR_1.METHOD_1(name);
    java.util.Calendar VAR_2 = null;
    if (date != null) {
        VAR_2 = java.util.Calendar.getInstance();
        VAR_2.METHOD_2(date);
    }
    VAR_1.METHOD_3(VAR_2);
    return VAR_1;
}"""

# Generate compressed version
print("RAW TOKEN COUNT:", len(example.split()))
for ratio in [0.1, 0.3, 0.5, 0.7, 0.9]:
    compressed = builder._priority_greedy_remove(example, ratio)
    print(f"\n--- Ratio {ratio} ---")
    print(compressed)
