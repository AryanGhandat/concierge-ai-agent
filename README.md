# Concierge AI — Email Summarizer & Task Planner Agent

This repository contains a submission-ready Kaggle/Colab project for the **Concierge Agents** track of the Kaggle Agents Intensive Capstone Project.
The agent summarizes emails and extracts actionable tasks (priority + due date).

## What's included
- `notebook.ipynb` — runnable Kaggle/Colab notebook (demo + code)
- `agent.py` — modular agent code (OpenAI + rule-based fallback)
- `emails.csv` — sample email dataset
- `email_agent_output.csv` — example output (generated after running)
- `requirements.txt` — Python dependencies
- `thumbnail_560x280.png` — project thumbnail for Kaggle card (if available)
- `README.md` — this file

## How to run
1. (Optional) Set `OPENAI_API_KEY` in your environment for the OpenAI-powered mode.
2. Open `notebook.ipynb` in Colab or Kaggle and run all cells.
3. If you do not provide an API key, the notebook uses a rule-based fallback extraction mode.

## License
MIT
