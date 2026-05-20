# WebCheck — AI Website Quality Tester

Paste any website URL and get an instant automated quality report powered by AI.

## Live App
🔗 [https://webbugreport.streamlit.app/](https://webbugreport.streamlit.app/)

## What the app does

WebCheck runs 7 automated checks on any website:

- ✅ Is the site reachable?
- ✅ How fast does it load?
- ✅ Is HTTPS enabled?
- ✅ Does it have a title tag?
- ✅ Does it have a meta description?
- ✅ Is it mobile friendly?
- ✅ Do all images have alt text?

After the checks, the results are sent to **Claude AI** which generates a short professional quality report with a score, issues to fix, and quick wins.

## How AI was used

This project was built using a vibe-coding approach with **Claude AI (claude.ai)**:
- Claude wrote the entire Python backend and Streamlit UI
- Claude AI API (claude-haiku) is used inside the app to generate the quality report
- Prompts were refined through conversation with Claude to improve output quality

## How to run locally

**Step 1** — Clone the repo
```
git clone https://github.com/YOUR_USERNAME/webcheck
cd webcheck
```

**Step 2** — Install dependencies
```
pip install -r requirements.txt
```

**Step 3** — Add your API key

Open `.streamlit/secrets.toml` and replace `paste-your-key-here` with your key from console.anthropic.com

**Step 4** — Run the app
```
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Tech used
- Python
- Streamlit
- Requests
- Claude AI (Anthropic)

## Author
Shivansh Mudgal — [LinkedIn](https://linkedin.com/in/shivansh-mudgal)
