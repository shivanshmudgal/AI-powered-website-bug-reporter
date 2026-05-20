# WebCheck — AI-Powered Website Bug Reporter

An automated website quality testing tool that runs multiple checks on any URL and generates a professional QA report using Claude AI.

## Live Demo
🔗 [Link to live app]

## What it does

Paste any website URL and WebCheck automatically runs 7 quality checks:

| Check | What it tests |
|-------|--------------|
| Site reachability | HTTP status code + response time |
| Load time | Flags slow sites (>2s warn, >4s fail) |
| HTTPS | Checks for secure SSL connection |
| Title tag | Verifies `<title>` exists |
| Meta description | Checks for SEO meta description |
| Mobile viewport | Verifies mobile-friendly viewport tag |
| Image alt tags | Counts images missing accessibility alt text |

After running the checks, it sends the results to **Claude AI (claude-haiku)** which generates a professional QA bug report with executive summary, critical issues, warnings, and recommended next steps.

## How AI was used in development

This project was built using **AI-assisted development**:
- **Claude AI (Anthropic)** — used to generate the Flask backend logic, automated check functions, and HTML/CSS frontend
- **Claude AI API** — integrated into the app itself to generate intelligent QA reports from raw test results
- The entire development workflow used a "vibe coding" approach — describing requirements to Claude and iterating on the output

## Tech Stack

- **Python** — core language
- **Flask** — web framework
- **Requests** — HTTP library for website checking
- **Claude AI API** — AI-generated QA reports
- **Deployed on Render** (free tier)

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/website-bug-reporter
cd website-bug-reporter
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Deploy to Render (free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variable: `ANTHROPIC_API_KEY = your_key_here`
5. Deploy — done!

## Author

Shivansh Mudgal — [LinkedIn](https://linkedin.com/in/shivansh-mudgal) | [GitHub](https://github.com/YOUR_USERNAME)
