import pandas as pd

df = pd.read_csv(
    "data/cleaned_newdata.csv",
    encoding="utf-8"
)

df.to_csv(
    "data/cleaned_newdata_utf8.csv",
    index=False,
    encoding="utf-8"
)

print("UTF8 cleaned file created!")