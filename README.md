# Lee Kuan Yew Chatbot (Monolith RAG System)

An interactive, responsive RAG (Retrieval-Augmented Generation) chatbot designed to emulate the pragmatism, directness, and governance philosophy of Singapore's founding father, **Lee Kuan Yew**.

Built as a lightweight Python/FastAPI monolith, this project includes a FAISS vector search database, dual-LLM API providers (OpenAI & Gemini), automatic fallback pipelines, and a live AI-judged Evaluation Dashboard.

---

## 🚀 Key Features

* **Dual LLM Provider Support**: Toggle seamlessly between **OpenAI (GPT-4o)** and **Google Gemini (1.5 Flash)**.
* **Resilient Fallback Pipeline**: 
  * If the primary provider hits quota limits or returns errors, it automatically falls back to the secondary provider.
  * If both providers fail or are unconfigured, it defaults to a **Local RAG Fallback Engine** that generates responses locally from retrieved text chunks.
* **Hybrid Search Engine**: Choose between **Local Keyword Search (token-overlap)** and **Vector RAG (FAISS Index)** utilizing a local HuggingFace embeddings model (`all-MiniLM-L6-v2`).
* **AI Evaluation Dashboard**: Features a live judge timeline scoring every response on:
  * **Context Relevance**: How well the response utilizes retrieved historical context.
  * **Persona Faithfulness**: How accurately the chatbot emulates Lee Kuan Yew's direct and stern tone.
* **Premium Dark UI**: An immersive, custom-styled frontend with pre-selected historical themes (Survival, Leadership, Geopolitics, Nation Building) and suggested inquiries.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI, Uvicorn, LangChain, FAISS (CPU), BeautifulSoup4 (for web scraping quotes)
* **Frontend**: HTML5, JS (Vanilla ES6), Tailwind CSS (via CDN), FontAwesome Icons, Marked.js (Markdown parser)
* **Embeddings**: Local HuggingFace Embeddings (`all-MiniLM-L6-v2`)
* **LLM APIs**: OpenAI API (`gpt-4o`/`gpt-4o-mini` for evaluation) and Google Gemini API (`gemini-1.5-flash`)

---

## 📋 Prerequisites

Before getting started, make sure you have:
* Python 3.10 or higher installed.
* An OpenAI API Key and/or a Google Gemini API Key.

---

## ⚙️ Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shevaardhana/LeeKuanYew-AI.git
cd LeeKuanYew-AI
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` template to create your `.env` file:
```bash
cp .env.example .env
```
Open the newly created `.env` file and insert your API keys:
```env
OPENAI_API_KEY="your_openai_api_key_here"
GEMINI_API_KEY="your_gemini_api_key_here"
PORT=8000
```
*(Note: `.env` is ignored by git to keep your keys secure).*

---

## 运行 (Running the Application)

### 1. (Optional) Rebuild the Vector Index
The repository comes pre-loaded with a FAISS index containing high-quality seed speeches, memoirs, and Wikiquote quotes. If you want to scrap quotes again and re-generate the embeddings:
```bash
python ingest.py
```

### 2. Start the FastAPI Server
Run the application using:
```bash
python main.py
```
Or run it directly with Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Open the Web Application
Navigate to **`http://localhost:8000`** in your browser.

---

## 🔍 How to Use the App

1. **Ask Questions**: Type your own inquiries or click on any of the **Suggested Inquiries** in the left sidebar.
2. **Switch Themes**: Toggle between themes (e.g., *Survival & Independence*, *Geopolitics*) to automatically update the suggested questions.
3. **Tune the RAG Engine**: Use the sidebar controls to:
   * Select your search algorithm (Keyword Match vs. FAISS Vector search).
   * Choose your preferred LLM provider (OpenAI vs. Gemini).
   * Adjust the retrieval chunk size ($k$).
4. **Monitor the Dashboard**: Click **Dashboard** (or slide open the Evaluation Dashboard drawer) to see real-time scores, feedback, and judges' rationale for the chatbot's answers.
