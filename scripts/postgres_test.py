import os
from dotenv import load_dotenv

load_dotenv()
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

query = "SELECT * FROM jobs"

df = pd.read_sql(query, conn)

skills = df["skill"].value_counts()

skills.plot(kind="bar")

plt.title("Top Skills")
plt.xlabel("Skills")
plt.ylabel("Number of Jobs")

plt.show()

conn.close()