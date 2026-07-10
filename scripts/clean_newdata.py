import pandas as pd

df = pd.read_csv("data/Newdata.csv")
df = df.dropna(subset=["Company Name"])

print(df.isnull().sum())

df = df.drop_duplicates()

print("Rows after cleaning:", len(df))

df.to_csv("data/cleaned_newdata.csv", index=False)

print("Cleaned file saved!")

