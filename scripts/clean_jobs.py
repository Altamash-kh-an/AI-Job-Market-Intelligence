import pandas as pd

df = pd.read_csv("data/jobs.csv")

print("Before Cleaning:", len(df))

df = df.drop_duplicates()

print("After Cleaning:", len(df))

print(df)

df.to_csv("data/cleaned_jobs.csv", index=False)

df.to_csv("data/cleaned_job.csv")