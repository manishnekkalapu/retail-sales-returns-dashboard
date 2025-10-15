import pandas as pd

# Load sales data
df = pd.read_csv("data/sample_sales.csv")

# Basic cleaning
df.dropna(inplace=True)

# Calculate total sales
df["Total"] = df["Quantity"] * df["UnitPrice"]

print("✅ Data cleaned and total sales calculated.")
print(df.head())
