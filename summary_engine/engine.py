import google.generativeai as genai
import pandas as pd
from PIL import Image


print("Library imported successfully!")


image_path = "anomaly_analysis_results.png"  # Your chart image
img = Image.open(image_path)

image_path1 = r"C:\Users\admin\Documents\GitHub\ray\regression_model_visualization.png"  # Your chart image
img1 = Image.open(image_path1)

df = pd.read_csv(r"C:\Users\admin\Documents\GitHub\ray\anomalous_power_data.csv")
print(df.head())  # check if it loaded properly
df1 = pd.read_csv(r"C:\Users\admin\Documents\GitHub\ray\anomalous_weather_data.csv")
print(df1.head())  # check if it loaded properly
prompt = f"""
You are an expert summarizer and analyst.
use the graph provided for better data analysis
Given the following content, generate a comprehensive structured report with the following sections:
(it is completely normal for irradiation to be 0 often because that represents either nighttime or extremely cloudy situations)
1. 🔹 Short Summary (2-3 lines): A quick, high-level takeaway.
2. 🔹 Overview: A paragraph explaining the main topic or theme.
3. 🔹 Cause Analysis: Break down the reasons, factors, or causes behind key points or events.
4. 🔹 Recommendations: Actionable suggestions or next steps based on the content.
5. 🔹 Detailed Summary: A deeper dive summarizing all the important information in a logical flow.
6. 🔹 Values: give the values(only give what is asked for do not provide any non essential note or explination here): such as perfromance ratio(estimate it), capacity factor, total yield (estimate), no. of anomalies detected, downtime(night time or clowdy weather), system health(good,bad) (no long sentences only values)

Here is the content the generation data along witht he weather data:
---
{df}
{df1}
---

Focus on real metrics


Avoid vague fluff like "could be due to"

Think like an energy analyst

Be less wordy, more impactful

Structure your output clearly with section headers. Be clear, concise, and informative. know that the summary is to be read by data analysts and managers.
Avoid repeating yourself. Be technical, precise, and practical.
"""

genai.configure(api_key= "AIzaSyAhy9yNA3B2_nb2D81QSkJbh7fto6m2esQ")


model = genai.GenerativeModel("gemini-1.5-flash")


response = model.generate_content(prompt)

with open("gemini_summary.txt", "w", encoding="utf-8") as f:
    f.write(response.text)


# Print the response
print(response.text)