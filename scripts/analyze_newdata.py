import pandas as pd

df = pd.read_csv("data/cleaned_newdata.csv")

print("Rows:", len(df))

print("\nTop 10 Locations:")
print(df["Location"].value_counts().head(10))

print("\nTop 10 Job Roles:")
print(df["Job Roles"].value_counts().head(10))

print("\nTop 10 Companies:")
print(df["Company Name"].value_counts().head(10))