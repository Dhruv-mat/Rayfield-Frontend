import google.generativeai as genai
import pandas as pd


print("Library imported successfully!")


df = pd.read_csv(r"C:\Users\admin\Documents\GitHub\ray\summary_engine\bt.csv")
print(df.head())  # check if it loaded properly

prompt = f"""
You are an expert summarizer and analyst.

Given the following content, generate a comprehensive structured report with the following sections:

1. 🔹 Short Summary (2-3 lines): A quick, high-level takeaway.
2. 🔹 Overview: A paragraph explaining the main topic or theme.
3. 🔹 Cause Analysis: Break down the reasons, factors, or causes behind key points or events.
4. 🔹 Recommendations: Actionable suggestions or next steps based on the content.
5. 🔹 Detailed Summary: A deeper dive summarizing all the important information in a logical flow.

Here is the content:
---
{df}
---
Structure your output clearly with section headers. Be clear, concise, and informative.
"""

genai.configure(api_key= "AIzaSyAhy9yNA3B2_nb2D81QSkJbh7fto6m2esQ")


model = genai.GenerativeModel("gemini-1.5-flash")


response = model.generate_content(prompt)

# Print the response
print(response.text)