import os
import pandas as pd
import matplotlib.pyplot as plt

# Ensure artifacts directory exists
os.makedirs("artifacts", exist_ok=True)

# Read original CSV
original_df = pd.read_csv("data/data-Sensor-1.csv")

# Read cleaned JSON
cleaned_df = pd.read_json("data-cleaned.json")

# Select an appropriate numeric column (first numeric column present in both)
original_numeric = original_df.select_dtypes(include="number")
cleaned_numeric = cleaned_df.select_dtypes(include="number")

common_numeric_cols = [col for col in original_numeric.columns if col in cleaned_numeric.columns]

if not common_numeric_cols:
    raise ValueError("No common numeric columns found between original and cleaned data.")

col = common_numeric_cols[0]

# Prepare data (align lengths if necessary by truncating to the shortest)
min_len = min(len(original_df), len(cleaned_df))
original_series = original_df[col].iloc[:min_len].reset_index(drop=True)
cleaned_series = cleaned_df[col].iloc[:min_len].reset_index(drop=True)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(original_series.index, original_series.values, color="blue", label="Original")
plt.plot(cleaned_series.index, cleaned_series.values, color="green", label="Cleaned")

plt.title(f"Original vs Cleaned Data for '{col}'")
plt.xlabel("Index")
plt.ylabel(col)
plt.legend()

# Save plot
plt.savefig("artifacts/data_visualization.png", bbox_inches="tight")
plt.close()