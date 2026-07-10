import pandas as pd

df = pd.read_csv("data/Newdata.csv")

print(df.head())
print("\nColumns:")
print(df.columns)

print("\nShape:")
print(df.shape)