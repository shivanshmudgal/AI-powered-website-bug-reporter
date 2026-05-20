import streamlit as st
import requests
import time
import re
import os

st.set_page_config(page_title="WebCheck — AI Website Bug Reporter", page_icon="🔍", layout="centered")

st.title("🔍 WebCheck — AI Website Bug Reporter")
st.caption("Enter any website URL to run automated quality checks and get an AI-generated bug report.")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def check_website(url):
    if not url.startswith("http"):
        url = "https://" + url
    result = {"url": url, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": []}
    try:
        start = time.time()
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        elapsed = round((time.time() - start) * 1000)

        result["checks"].append(("Site reachability", "pass" if r.status_code < 400 else "fail", f"HTTP {r.status_code} in {elapsed}ms"))
        result["checks"].append(("Load time", "pass" if elapsed < 2000 else "warn" if elapsed < 4000 else "fail", f"{elapsed}ms"))
        result["checks"].append(("HTTPS enabled", "pass" if url.startswith("https") else "fail", "Secure" if url.startswith("https") else "No SSL"))
        result["checks"].append(("Page title tag", "pass" if "<title>" in r.text.lower() else "fail", "Found" if "<title>" in r.text.lower() else "Missing <title>"))
        has_meta = 'name="description"' in r.text.lower()
        result["checks"].append(("Meta description", "pass" if has_meta else "warn", "Found" if has_meta else "Missing — bad for SEO"))
        has_vp = "viewport" in r.text.lower()
        result["checks"].append(("Mobile viewport", "pass" if has_vp else "warn", "Found" if has_vp else "Missing — not mobile friendly"))
        imgs = re.findall(r'<img[^>]*>', r.text, re.IGNORECASE)
        no_alt = sum(1 for i in imgs if "alt=" not in i.lower())
        result["checks"].append(("Image alt tags", "pass" if no_alt == 0 else "warn", f"{no_alt} missing alt text" if no_alt else "All images have alt tags"))

    except requests.exceptions.ConnectionError:
        result["checks"].append(("Site reachability", "fail", "Could not connect"))
    except requests.exceptions.Timeout:
        result["checks"].append(("Site reachability", "fail", "Timed out after 10s"))
    except Exception as e:
        result["checks"].append(("Site reachability", "fail", str(e)))

    return result


def generate_ai_report(result):
    passes = sum(1 for _, s, _ in result["checks"] if s == "pass")
    warns  = sum(1 for _, s, _ in result["checks"] if s == "warn")
    fails  = sum(1 for _, s, _ in result["checks"] if s == "fail")

    if not ANTHROPIC_API_KEY:
        lines = "\n".join([f"- **{n}** [{s.upper()}]: {d}" for n, s, d in result["checks"]])
        return (
            f"### Summary\n{passes} passed · {warns} warnings · {fails} failed\n\n"
            f"### Findings\n{lines}\n\n"
            f"### Recommendation\nFix all FAIL items immediately. Review WARN items for improvement."
        )

    checks_text = "\n".join([f"- {n}: {s.upper()} — {d}" for n, s, d in result["checks"]])
    prompt = (
        f"You are a QA automation engineer. Analyze this website test report.\n\n"
        f"URL: {result['url']}\nTested: {result['timestamp']}\n\nChecks:\n{checks_text}\n\n"
        f"Write a professional QA bug report with: 1) Executive summary 2) Critical issues "
        f"3) Warnings 4) What passed 5) Next steps. Use markdown, be concise."
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"AI report unavailable: {e}"


# --- UI ---

url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("🚀 Run Check", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("Running automated checks..."):
            result = check_website(url.strip())

        # Summary metrics
        passes = sum(1 for _, s, _ in result["checks"] if s == "pass")
        warns  = sum(1 for _, s, _ in result["checks"] if s == "warn")
        fails  = sum(1 for _, s, _ in result["checks"] if s == "fail")

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Passed", passes)
        c2.metric("⚠️ Warnings", warns)
        c3.metric("❌ Failed", fails)

        st.subheader("Check Results")
        for name, status, detail in result["checks"]:
            if status == "pass":
                st.success(f"**{name}** — {detail}")
            elif status == "warn":
                st.warning(f"**{name}** — {detail}")
            else:
                st.error(f"**{name}** — {detail}")

        st.subheader("🤖 AI Quality Report")
        with st.spinner("Generating AI report..."):
            report = generate_ai_report(result)
        st.markdown(report)

        st.caption(f"Checked: {result['url']} at {result['timestamp']}")

st.divider()
st.caption("Built with Python · Streamlit · Claude AI — by Shivansh Mudgal")
