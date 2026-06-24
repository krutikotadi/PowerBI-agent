# ⚡ Power BI Dashboard Agent

A small tool that turns a typed dashboard request into a working preview — plus the DAX code to build it for real.

> Type something like *"show me how sales are doing across regions"* and you get a live interactive dashboard, a quick breakdown of what's worth looking at, and — if you ask — the actual DAX code to build it in Power BI.

---

## 📸 Demo

![App demo](screenshots/demo.png)

*(Screenshot coming soon — see [Setup](#-setup--run-locally) below to run it yourself.)*

---

## 🧠 Why I Built This

I wanted to see if I could speed up the gap between "here's what I want" and "here's the actual dashboard" — describe what you need, get a working preview right away, then ask for the DAX when you're ready to actually build it in Power BI.

It's a personal project, not a production tool — mostly something I built to learn, and to try out how much manual reporting work AI can realistically take off your plate.

---

## ✨ What It Does

- **Just describe what you want** — type something like "build me an HR dashboard to track attrition" and it builds a live, interactive preview with Plotly.
- **Two ways it responds:**
  - 💬 **Explain mode (default)** — talks you through what the dashboard shows, what to watch for, likely reasons behind the numbers, and a few follow-up questions worth asking.
  - 🧮 **DAX mode** — say "DAX," "measures," or "code" and it gives you the real implementation: assumptions about your data, the actual DAX measures, layout suggestions, a few design tips, and ideas for what to add next.
- **Recognizes what kind of dashboard you're asking for** — sales by region, product performance, financials, HR/attrition, marketing campaigns, customer support — and builds the right charts for it automatically.
- **Runs entirely on your own machine** — no API keys, no cloud calls. Just [Ollama](https://ollama.com/) running Llama 3.2 locally.

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| Visualization | [Plotly](https://plotly.com/python/) |
| Data | [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) (simulated sample dataset) |
| AI/agent logic | [LangChain](https://www.langchain.com/) |
| LLM runtime | [Ollama](https://ollama.com/) running **Llama 3.2**, fully local |

---

## 🚀 Setup & Run Locally

### 1. Install Ollama and pull the model
This app needs [Ollama](https://ollama.com/download) installed and running locally.

```bash
# After installing Ollama, pull the model used by this app:
ollama pull llama3.2
```

Make sure Ollama is running in the background before starting the app.

### 2. Clone the repo and install Python dependencies

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 💡 Example Prompts to Try

- "I want to see how sales are doing across regions"
- "Show me which products are underperforming"
- "Why are these products underperforming?"
- "Build me an HR dashboard to track employee attrition"
- "I need a financial dashboard showing revenue vs expenses"
- "Now give me the DAX measures for this dashboard"

---

## 📁 Project Structure

```
.
├── app.py            # Streamlit UI + chart/dashboard generation logic
├── pbi_agent.py       # LangChain + Ollama agent (explain mode & DAX mode)
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 🔍 How It Works

1. **`app.py`** builds a sample sales dataset (regions, products, categories, revenue, cost, profit, targets) and looks at what you typed to figure out which charts make sense — region, product, time trend, financial, HR, marketing, or support.
2. **`pbi_agent.py`** checks whether you're asking for an explanation or actual code (`wants_dax()`), then sends your question to the right prompt — one for talking through the dashboard in plain terms, the other for writing real, structured DAX.
3. It all runs through Ollama on your own machine, so there's no API key and nothing leaves your computer.

---

## 🧩 What I'd Add Next

- Hook it up to a real data source instead of sample data
- Let people upload their own CSV/Excel files
- Make the routing smarter than just keyword matching
- Export the insights to PDF or PowerPoint

---

Built by **Kruti Kotadia** — [https://www.linkedin.com/in/kruti-kotadia/](#) 
