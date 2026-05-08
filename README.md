# -10k-financial-chatbot-
# 📈 AI Financial Analysis Chatbot (10-K Analyzer)

> Ask questions about company financials in plain English — no SQL, no spreadsheets, no finance degree required.

Built as part of the **BCG X GenAI Job Simulation** on Forage. Evolved from a rule-based prototype into a full dynamic analysis tool with an interactive UI.

---

## 🚀 Live Demo

```bash
git clone https://github.com/YOUR_USERNAME/10k-financial-chatbot
cd 10k-financial-chatbot
pip install -r requirements.txt
streamlit run app.py
```

---

## 💡 What It Does

| Feature | Description |
|---|---|
| 🗣️ Natural Language Queries | Ask questions like *"Compare Apple and Tesla revenue"* — no rigid commands |
| 📊 Dynamic Charts | Auto-generates line, bar, and multi-panel charts via Plotly |
| 🔄 YoY Growth Analysis | Calculates year-over-year % change for any metric |
| 🆚 Multi-Company Comparison | Compare up to N companies across any metric and year |
| 📉 Profit Margin Analysis | Net margin trends across companies and years |
| 📂 CSV Upload | Bring your own financial data — works with any structured CSV |
| 🏆 Best/Worst Ranking | *"Which company has the highest net income?"* |
| 📋 Overview Dashboard | 4-panel summary chart (Revenue, Net Income, EPS, Margin) |

---

## 🧠 Architecture

```
app.py          ← Streamlit UI (chat interface, KPI strip, sample questions)
engine.py       ← Analysis engine (query parsing, data analysis, chart generation)
data/
  sample_financials.csv  ← Apple, Microsoft, Tesla, Amazon (2020–2023)
requirements.txt
```

**engine.py** uses keyword + intent detection (no LLM dependency) to:
1. Detect companies mentioned in the query
2. Detect the financial metric (revenue, EPS, margin, etc.)
3. Detect the intent (compare, growth, summary, rank)
4. Return a text answer + Plotly chart

---

## 📸 Sample Queries

```
"What is Apple's total revenue?"
"Compare Apple and Microsoft net income in 2023"
"Show revenue growth for all companies"
"Which company has the highest profit margin?"
"What is Tesla's EPS trend?"
"Show me a summary dashboard"
"Compare Apple and Amazon EPS in 2022"
"What is Microsoft's R&D expense?"
```

---

## 📊 Sample Data Included

Pre-loaded with 4 companies × 4 years (2020–2023):

| Company | Metrics Covered |
|---------|----------------|
| Apple | Revenue, Net Income, EPS, Assets, Liabilities, R&D, Cash Flow, Gross Profit |
| Microsoft | ↑ same |
| Tesla | ↑ same |
| Amazon | ↑ same |

**Bring your own data** by uploading any CSV with columns: `Company, Year, Revenue, Net_Income, EPS` (plus any extras).

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — web UI
- **Pandas** — data manipulation & analysis
- **Plotly** — interactive charts

No external APIs. No LLM costs. Runs fully offline.

---

## 🔮 Roadmap

- [ ] PDF / 10-K report parsing (extract tables automatically)
- [ ] OpenAI / Claude API integration for true NLP
- [ ] Export analysis as PDF report
- [ ] Stock price overlay via yfinance
- [ ] Ratio analysis (P/E, Debt-to-Equity, ROE)

---

## 👤 Author

**Priyanshu Sajwan**  
BCG X GenAI Job Simulation — Certificate of Completion (May 2026)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com)

---

## 📄 License

MIT — free to use, fork, and extend.
