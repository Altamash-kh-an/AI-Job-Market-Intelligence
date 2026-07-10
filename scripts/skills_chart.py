import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/jobs.csv")

skills = df["Skill"].value_counts()

skills.plot(kind="pie")

plt.title("Top Skills")
plt.xlabel("Skills")
plt.ylabel("Number of Jobs")

plt.show()