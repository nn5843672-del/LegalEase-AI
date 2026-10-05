# LegalEase — AI Legal Document Studio

A student project that creates editable agreement drafts, with TXT, DOCX and PDF downloads.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   uvicorn backend.app.main:app --reload
   ```

3. Open http://127.0.0.1:8000 in your browser.

The app works in demo mode without an API key. For AI-generated drafts, add your Google AI Studio key to `GEMINI_API_KEY` in `.env`, then restart the server. Keep `.env` private.

## Main features

- Responsive LegalEase web interface
- NDA, freelance, lease, employment and custom agreement drafts
- Gemini API integration, with a demo fallback
- Editable draft preview
- TXT, DOCX and PDF export
- Draft review notice for legal safety

This project produces drafting aids for learning. It does not provide legal advice; have a qualified legal professional review documents before use.
