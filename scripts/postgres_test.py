import matplotlib.pyplot as plt
import pandas as pd

from api.database import get_connection

conn = get_connection()
try:
    df = pd.read_sql("SELECT job_roles FROM pan_india_jobs", conn)
finally:
    conn.close()

job_roles = df["job_roles"].value_counts()
job_roles.plot(kind="bar")

plt.title("Top Job Roles")
plt.xlabel("Job Roles")
plt.ylabel("Number of Jobs")

plt.show()
