import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from telegram import Update
from telegram.ext import ContextTypes

conn = sqlite3.connect("database.db")
c = conn.cursor()
df = pd.read_sql_query("SELECT * FROM weekly_feedback", conn)

output_dir = "."
pdf_path = os.path.join(output_dir, "Weekly_Feedback_Report.pdf")

def plot_percentage_chart(series, title, filename, color):
    value_counts = series.value_counts(normalize=True) * 100
    plt.figure(figsize=(5, 3))
    value_counts.plot(kind='bar', color=color)
    plt.title(title)
    plt.ylabel("Percentage (%)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    chart_path = os.path.join(output_dir, filename)
    plt.savefig(chart_path)
    plt.close()
    return chart_path

chart_paths = []
if 'conflict' in df.columns:
    chart_paths.append(plot_percentage_chart(df['conflict'], "Conflict Reports", "conflict_chart.png", 'lightcoral'))
if 'support' in df.columns:
    chart_paths.append(plot_percentage_chart(df['support'], "Support Needed", "support_chart.png", 'lightgreen'))

pdf = FPDF()
pdf.add_page()
pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
pdf.set_font("DejaVu", "", 14)
pdf.cell(200, 10, "MoodDetection - Weekly HR Report", ln=True, align="C")
pdf.ln(10)

for chart in chart_paths:
    if os.path.exists(chart):
        pdf.image(chart, x=30, w=150)
        pdf.ln(10)

pdf.set_font("DejaVu", "", 12)
pdf.cell(200, 10, "Employee Comments & Suggestions:", ln=True)
pdf.ln(5)
pdf.set_font("DejaVu", size=10)

c.execute("SELECT username, comment FROM weekly_feedback WHERE comment != '' ORDER BY timestamp DESC")
comments = c.fetchall()
pdf.set_font("DejaVu", "", 10)
for username, comment in comments:
    pdf.multi_cell(0, 8, f"— {username}:\n{comment.strip()}")
    pdf.ln(1)

conn.close()
pdf.output(pdf_path)
print(f" PDF generated: {pdf_path}")

async def generate_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pdf.output("Weekly_Feedback_Report.pdf")
    with open("Weekly_Feedback_Report.pdf", "rb") as pdf_file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)