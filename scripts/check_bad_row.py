import pandas as pd

df = pd.read_csv("data/cleaned_newdata.csv", encoding="utf-8")

print(df.iloc[18155:18165])