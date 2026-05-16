# CodePromptZip Evaluation Results

## Results Table

| Configuration | τ_code | Shots | Compression | CodeBLEU | Actual τ% | Avg Tokens (Orig→Comp) |
|---|---|---|---|---|---|---|
| no_compress_shots_1 | 0.0 | 1 | ✓ | 88.3 | N/A | N/A |
| no_compress_shots_2 | 0.0 | 2 | ✓ | 88.6 | N/A | N/A |
| no_compress_shots_3 | 0.0 | 3 | ✓ | 88.7 | N/A | N/A |
| tau_0.0_shots_1 | 0.0 | 1 | ✓ | 88.3 | N/A | N/A |
| tau_0.1_shots_1 | 0.1 | 1 | ✓ | 87.1 | -4.1 | 160→167 |
| tau_0.2_shots_1 | 0.2 | 1 | ✓ | 87.3 | 7.5 | 160→148 |
| tau_0.3_shots_0 | 0.3 | 0 | ✓ | 88.1 | N/A | N/A |
| tau_0.3_shots_1 | 0.3 | 1 | ✓ | 87.9 | 18.6 | 160→130 |
| tau_0.3_shots_2 | 0.3 | 2 | ✓ | 87.6 | 18.7 | 322→262 |
| tau_0.3_shots_3 | 0.3 | 3 | ✓ | 87.3 | 18.7 | 484→393 |
| tau_0.5_shots_1 | 0.5 | 1 | ✓ | 88.4 | 40.9 | 160→94 |
| tau_0.7_shots_1 | 0.7 | 1 | ✓ | 88.3 | 63.3 | 160→58 |
| tau_0.9_shots_1 | 0.9 | 1 | ✓ | 88.4 | 87.0 | 160→20 |

## LaTeX Table (copy-paste into your report)

```latex
\begin{table}[h]
\centering
\caption{CodePromptZip Evaluation Results on Bugs2Fix}
\label{tab:results}
\begin{tabular}{lccccc}
\toprule
Configuration & $\tau_{code}$ & Shots & Compression & CodeBLEU & Token Savings \\
\midrule
no_compress_shots_1 & 0.0 & 1 & \checkmark & 88.3 & N/A \\
no_compress_shots_2 & 0.0 & 2 & \checkmark & 88.6 & N/A \\
no_compress_shots_3 & 0.0 & 3 & \checkmark & 88.7 & N/A \\
tau_0.0_shots_1 & 0.0 & 1 & \checkmark & 88.3 & N/A \\
tau_0.1_shots_1 & 0.1 & 1 & \checkmark & 87.1 & -4.1\% \\
tau_0.2_shots_1 & 0.2 & 1 & \checkmark & 87.3 & 7.5\% \\
tau_0.3_shots_0 & 0.3 & 0 & \checkmark & 88.1 & N/A \\
tau_0.3_shots_1 & 0.3 & 1 & \checkmark & 87.9 & 18.6\% \\
tau_0.3_shots_2 & 0.3 & 2 & \checkmark & 87.6 & 18.7\% \\
tau_0.3_shots_3 & 0.3 & 3 & \checkmark & 87.3 & 18.7\% \\
tau_0.5_shots_1 & 0.5 & 1 & \checkmark & 88.4 & 40.9\% \\
tau_0.7_shots_1 & 0.7 & 1 & \checkmark & 88.3 & 63.3\% \\
tau_0.9_shots_1 & 0.9 & 1 & \checkmark & 88.4 & 87.0\% \\
\bottomrule
\end{tabular}
\end{table}
```