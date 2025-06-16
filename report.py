#PDF construction
from nlp_units import classify_comment
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from telegram import Update
from telegram.ext import ContextTypes
#from transformers import AutoTokenizer, AutoModelForSequenceClassification
#import torch

# model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

#tokenizer = AutoTokenizer.from_pretrained(model_name)
#model = AutoModelForSequenceClassification.from_pretrained(model_name)

#labels = ['Negative', 'Neutral', 'Positive']

#def classify_comment(text):
    #inputs = tokenizer(text, return_tensors="pt", truncation=True)
    #with torch.no_grad():
        #outputs = model(**inputs)
    #probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    #predicted = torch.argmax(probs, dim=1).item()
    #return labels[predicted], float(probs[0][predicted])


conn = sqlite3.connect("database.db")
df = pd.read_sql_query("SELECT * FROM daily_feedback", conn)
conn.close()

chart_path = None
if 'mood' in df.columns and not df['mood'].dropna().empty:
    mood_counts = df['mood'].value_counts()

    plt.figure(figsize=(6, 4))
    mood_counts.plot(kind='bar', color='skyblue')
    plt.title("Mood Distribution")
    plt.xlabel("Mood")
    plt.ylabel("Count")
    plt.tight_layout()

    chart_path = "mood_chart.png"
    plt.savefig(chart_path)
    plt.close()

pdf = FPDF()
pdf.add_page()
pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
pdf.set_font("DejaVu", "", 14)
pdf.cell(200, 10, "MoodDetection Daily Report", ln=True, align="C")
pdf.ln(10)

if chart_path:
    pdf.image(chart_path, x=30, w=150)
    pdf.ln(10)

pdf.set_font("DejaVu", "", 10)
columns = df.columns.tolist()
for col in columns:
    pdf.cell(35, 8, col[:12], border=1)
pdf.ln()

pdf.set_font("DejaVu", size=10)
for _, row in df.iterrows():
    for col in columns:
        text = str(row[col])[:12]
        pdf.cell(35, 8, text, border=1)
    pdf.ln()

for _, row in df.iterrows():
    comment = row.get('comment')
    username = row.get('username', 'anon')
    
    if pd.notna(comment) and str(comment).strip():
        sentiment, confidence = classify_comment(comment)
        sentiment_line = f"{username} [{sentiment}] — {comment.strip()}"
        pdf.multi_cell(0, 8, sentiment_line)
        pdf.ln(1)

pdf.output("MoodDetection_Report.pdf")
print("Report saved as MoodDetection_Report.pdf")

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pdf.output("MoodDetection_Report.pdf")
    with open("MoodDetection_Report.pdf", "rb") as pdf_file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)