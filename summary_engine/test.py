import google.generativeai as genai
import pandas as pd


print("Library imported successfully!")



df = pd.read_csv("tt.csv")
print(df.head())  # check if it loaded properly

prompt = f"""
You are a senior data analyst.

Here is a dataset of anomalies detected by an ML model:

{df}

Generate:
1. A plain English summary
2. Analysis of likely causes
3. Suggested next steps
4. A clean report for stakeholders
"""

genai.configure(api_key= "AIzaSyAhy9yNA3B2_nb2D81QSkJbh7fto6m2esQ")

# Load the model (Gemini Pro for text)
model = genai.GenerativeModel("gemini-1.5-flash")

# Send a prompt to the model
response = model.generate_content(prompt)

# Print the response
print(response.text)