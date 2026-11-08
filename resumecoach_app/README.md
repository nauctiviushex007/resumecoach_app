# ResumeCoach (Streamlit, all Python)

```
resumecoach_app/
├── app.py                  # entry point (config, password gate, page layout)
├── backend/
│   ├── analysis.py         # keyword matching, resume checks (pure Python)
│   ├── ai.py               # optional LLM calls + guardrails against invented facts
│   └── files.py            # PDF / DOCX / TXT text extraction
├── frontend/
│   └── ui.py               # all Streamlit screens
├── tests/test_analysis.py
├── requirements.txt
└── .streamlit/secrets.toml.example
```

## Run locally (Windows PowerShell)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Optional AI: copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your key.

## Deploy on Streamlit Community Cloud
1. Push this whole folder to GitHub (secrets.toml is git-ignored).
2. share.streamlit.io -> Create app -> choose repo, branch, `app.py`.
3. Settings -> Secrets: `ANTHROPIC_API_KEY = "..."` and `APP_PASSWORD = "..."`.

## Safety
Prompts forbid invented facts, `[ADD METRIC]` replaces made-up numbers, new numbers are flagged, and nothing changes until you Accept.
Set `APP_PASSWORD` and a spend limit with your AI provider before making the app public.

## Tests
`pip install pytest` then `pytest -q`
