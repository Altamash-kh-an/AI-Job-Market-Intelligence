import pandas as pd

df = pd.read_csv("data/jobs.csv")

print("First 5 Rows:")
print(df.head())

print("\nTotal Jobs:", len(df))

print("\nJobs by Location:")
print(df["Location"].value_counts())

print("\nJobs by Skill:")
print(df["Skill"].value_counts())



print("\nAverage Experience:")
print(df["Experience"].mean())

print("\nMaximum Experience:")
print(df["Experience"].max())

print("\nMinimum Experience:")
print(df["Experience"].min())
