# VPDS Component Suggestion API (Backend)

This is the backend API for the **VPDS Component Suggestion Tool**, that allows users to input a natural language description (like _"login form with email input and submit button"_) and receive TSX code snippets using **Visa's Product Design System (VPDS)** components.

The backend interprets user intent and suggests appropriate component code by either:
- Looking it up from a cached dataset (csv file) (for known patterns)
- Or generating the result by combining known VPDS components

---

## Tech Stack

- **Python + FastAPI**: Chosen for its speed, simplicity, and modern async support. FastAPI allows clean routing, validation (via Pydantic), and scalability.
- **CSV caching (`pattern-dataset.csv`)**: Allows storing previously seen query/code pairs so repeat queries return instantly.
- **components.json**: A custom dataset mapping 33 component names to metadata and usage examples. Acts as the source of truth for generating JSX.
- **Optional OpenAI integration**: If `OPENAI_API_KEY` is provided, the API can fall back to AI-based generation using gpt-4o-mini (not required for core functionality). Currently has limited tokenzation for query requests. 

---

## What does it do?

- Accepts a plain English description (e.g., `"login form with remember me checkbox"`).
- Checks if it already exists in a cache (CSV file).
- If found, returns the TSX snippet and used VPDS components.
- If not found, attempts to match against the internal pattern rules (or optionally generate via OpenAI).
- Updates the CSV cache automatically with new patterns and results.

---

## 🗂 Project Structure
```
vpds-rec-backend/
├── app/
│ ├── main.py # FastAPI app, CORS setup, router registration
│ ├── routes.py # All route handlers (/api/suggest, /health, /status, etc.)
│ ├── assembler.py # Core logic: rule matching, cache reading/writing, snippet assembly
│ └── components.json # Metadata and code snippets for all supported VPDS components
├── pattern-dataset.csv # Auto-updating cache of query → components → snippet
├── requirements.txt # Python dependencies
├── README.md # You are here!
└── .env (optional) # Set OPENAI_API_KEY or USE_AI_MERGING here
```
---

## How to Run Locally

1. **Clone the backend repo**
```bash
git clone https://github.com/yourusername/vpds-rec-backend.git
cd vpds-rec-backend
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **(Optional) Create .env file**
```bash
OPENAI_API_KEY=your_openai_key_here
USE_AI_MERGING=true
```
4. **Run the server**
```bash
uvicorn app.main:app --reload
```
5. **(Optional) Testing**
```bash
curl -X POST http://127.0.0.1:8000/api/suggest \
  -H "Content-Type: application/json" \
  -d '{"query": "login form with email input"}'
```



   
