import pandas as pd

data = {
    "Job_Title": ["Data Engineer", "Python Developer", "AI Engineer"],
    "Location": ["Bangalore", "Pune", "Hyderabad"]
}

df = pd.DataFrame(data)

print(df)