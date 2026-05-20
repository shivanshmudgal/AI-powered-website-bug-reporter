from flask import Flask, render_template, request, jsonify
import requests
import time
import json
import os

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def check_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    result = {
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checks": []
    }
    # Check 1: reachability + response time
    try:
        start = time.time()
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        elapsed = round((time.time() - start) * 1000)
        result["checks"].append({
            "name": "Site reachability",
            "status": "pass" if r.status_code < 400 else "fail",
            "detail": f"HTTP {r.status_code} in {elapsed}ms"
        })
        result["status_code"] = r.status_code
        result["load_time_ms"] = elapsed
        result["html"] = r.text[:3000]

        # Check 2: load time
        result["checks"].append({
            "name": "Load time",
            "status": "pass" if elapsed < 2000 else "warn" if elapsed < 4000 else "fail",
            "detail": f"{elapsed}ms ({'fast' if elapsed < 2000 else 'slow' if elapsed >= 4000 else 'acceptable'})"
        })

        # Check 3: HTTPS
        result["checks"].append({
            "name": "HTTPS enabled",
            "status": "pass" if url.startswith("https") else "fail",
            "detail": "Secure connection" if url.startswith("https") else "No SSL — insecure"
        })

        # Check 4: title tag
        has_title = "<title>" in r.text.lower()
        result["checks"].append({
            "name": "Page title tag",
            "status": "pass" if has_title else "fail",
            "detail": "Title tag found" if has_title else "Missing <title> tag"
        })

        # Check 5: meta description
        has_meta = 'name="description"' in r.text.lower() or "name='description'" in r.text.lower()
        result["checks"].append({
            "name": "Meta description",
            "status": "pass" if has_meta else "warn",
            "detail": "Found" if has_meta else "Missing — bad for SEO"
        })

        # Check 6: viewport meta (mobile friendly)
        has_viewport = "viewport" in r.text.lower()
        result["checks"].append({
            "name": "Mobile viewport",
            "status": "pass" if has_viewport else "warn",
            "detail": "Viewport meta found" if has_viewport else "Missing viewport — may not be mobile friendly"
        })

        # Check 7: broken images placeholder check
        import re
        img_tags = re.findall(r'<img[^>]*>', r.text, re.IGNORECASE)
        no_alt = sum(1 for img in img_tags if "alt=" not in img.lower())
        result["checks"].append({
            "name": "Image alt tags",
            "status": "pass" if no_alt == 0 else "warn",
            "detail": f"{no_alt} image(s) missing alt attribute" if no_alt > 0 else "All images have alt tags"
        })

    except requests.exceptions.ConnectionError:
        result["checks"].append({"name": "Site reachability", "status": "fail", "detail": "Could not connect to site"})
        result["html"] = ""
        result["status_code"] = 0
        result["load_time_ms"] = 0
    except requests.exceptions.Timeout:
        result["checks"].append({"name": "Site reachability", "status": "fail", "detail": "Request timed out after 10s"})
        result["html"] = ""
        result["status_code"] = 0
        result["load_time_ms"] = 0

    return result


def generate_ai_report(check_result):
    if not ANTHROPIC_API_KEY:
        # Fallback: generate report without AI
        passes = sum(1 for c in check_result["checks"] if c["status"] == "pass")
        warns = sum(1 for c in check_result["checks"] if c["status"] == "warn")
        fails = sum(1 for c in check_result["checks"] if c["status"] == "fail")
        return f"""## Automated Test Report

**URL:** {check_result['url']}
**Tested at:** {check_result['timestamp']}

### Summary
- {passes} checks passed
- {warns} warnings
- {fails} failures

### Findings
""" + "\n".join([f"- **{c['name']}** [{c['status'].upper()}]: {c['detail']}" for c in check_result["checks"]]) + """

### Recommendation
Fix all FAIL items immediately. Review WARN items for improvement.
"""

    checks_text = "\n".join([f"- {c['name']}: {c['status'].upper()} — {c['detail']}" for c in check_result["checks"]])
    prompt = f"""You are a QA automation engineer. Analyze this website test report and write a professional bug/quality report.

URL tested: {check_result['url']}
Tested at: {check_result['timestamp']}

Automated checks:
{checks_text}

Write a clear, professional QA report with:
1. Executive summary (2-3 sentences)
2. Critical issues (if any)
3. Warnings to address
4. What passed
5. Recommended next steps

Keep it concise and actionable. Use markdown formatting."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = response.json()
        return data["content"][0]["text"]
    except Exception as e:
        return f"AI report unavailable: {str(e)}\n\nBasic results:\n" + "\n".join([f"- {c['name']}: {c['status']}" for c in check_result["checks"]])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check():
    url = request.json.get("url", "").strip()
    if not url:
        return jsonify({"error": "Please enter a URL"}), 400
    result = check_website(url)
    report = generate_ai_report(result)
    return jsonify({
        "checks": result["checks"],
        "report": report,
        "url": result["url"],
        "timestamp": result["timestamp"]
    })


if __name__ == "__main__":
    app.run(debug=True)
