# 🤖 Mega Coder — AI-Powered Coding Assistant

Your AI pair programmer: generate Python programs from plain English, fix and explore GitHub repos, and get **live coding tips** from your screen.

---

## ✨ What it does

- **📝 Generate Python programs** — Describe what you want; the assistant writes runnable code, runs it, fixes errors, optimizes, lints, and documents it.
- **🔧 Work with GitHub repos** — Paste a public repo URL and say what you want changed or explained; it ingests the repo and returns fixes or explanations.
- **👀 Real-time screen tips** — Point your screen at code; OCR + AI gives you improvement suggestions, optimizations, and refactor ideas.

Powered by **Gemini** (Flash-Lite for speed, Pro for repo analysis) and optional **OpenAI** test scripts.

---

## 🛠 Technologies Used

### AI & APIs
- **Google Gemini API** (`google-generativeai`) — Code generation, fixes, optimization, documentation, and repo analysis
- **OpenAI API** (`openai`) — Optional testing script for ChatGPT integration

### Code Quality & Execution
- **Pylint** — Static code analysis and linting
- **subprocess** — Running generated Python code dynamically

### GitHub Integration
- **GitIngest** (`gitingest`) — Ingesting and analyzing public GitHub repositories

### Screen Capture & OCR
- **MSS** (`mss`) — Cross-platform screenshot capture
- **OpenCV** (`opencv-python`, `cv2`) — Image processing for screenshots
- **NumPy** (`numpy`) — Image array manipulation
- **RapidOCR** (`rapidocr_onnxruntime`) — Optical Character Recognition for extracting code from screen

### UI & UX
- **Colorama** (`colorama`) — Colored terminal output
- **tqdm** (`tqdm`) — Progress bars for long-running operations

### Configuration
- **python-dotenv** (`dotenv`) — Environment variable management from `.env` files

### Core Python
- Standard library: `os`, `random`, `time`, `subprocess`

---

## 🛠 Setup

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**  
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   ```
   For the OpenAI tester script (optional):
   ```env
   OPENAI_API_KEY_UPDATED=your_openai_api_key
   ```

---

## 🚀 Run

```bash
python mega_coder.py
```

Choose from the menu:

1. **Develop a Python program** — Describe the program; get generated code, fixes, optimization, lint fixes, and docs.
2. **Fix/change something in a GitHub repository** — Provide repo URL + instruction; get analysis and suggested changes.
3. **Look at my screen and give realtime coding tips** — Show code on screen; get live improvement tips (press Ctrl+C to stop).
4. **Exit**

---

## 📁 Project layout

| File | Purpose |
|------|--------|
| `mega_coder.py` | Main app: menu, code generation, GitHub flow, screen tips |
| `gemini_tester.py` | Simple script to test Gemini API (prime-number code sample) |
| `chatgpt_response_tester.py` | Simple script to test OpenAI API (prime-number code sample) |

Generated artifacts (gitignored): `generated-code-gemini.py`, `generated-doc-gemini.txt`.

---

## 📋 Requirements

- Python 3.x
- Gemini API key (required for main features)
- Optional: OpenAI API key for the ChatGPT tester

See `requirements.txt` for Python packages (e.g. `google-generativeai`, `python-dotenv`, `gitingest`, `mss`, `opencv-python`, `rapidocr_onnxruntime`, `colorama`, `tqdm`, `pylint`).

---

## 📄 License

Use and modify as you like. No warranty.

---

*Built for developers who want an AI coding buddy in the terminal.* 🧑‍💻
