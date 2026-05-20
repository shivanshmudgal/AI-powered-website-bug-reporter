import streamlit as st
import requests
import time
import re

st.set_page_config(
    page_title="WebCheck - AI Website Tester",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 WebCheck")
st.subheader("AI-Powered Website Quality Tester")
st.write("Enter any website URL below. The app will run 7 automated checks and generate a quality report.")

st.divider()

url = st.text_input("Enter website URL", placeholder="https://example.com")

def run_checks(url):
    if not url.startswith("http"):
        url = "https://" + url

    results = []

    try:
        start = time.time()
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        load_time = round((time.time() - start) * 1000)
        html = response.text

        # Check 1: Is site reachable?
        if response.status_code < 400:
            results.append(("✅", "Site is reachable", f"Responded with HTTP {response.status_code}"))
        else:
            results.append(("❌", "Site not reachable", f"Got HTTP {response.status_code} error"))

        # Check 2: Load speed
        if load_time < 2000:
            results.append(("✅", "Load speed is good", f"Loaded in {load_time}ms"))
        elif load_time < 4000:
            results.append(("⚠️", "Load speed is slow", f"Took {load_time}ms — should be under 2000ms"))
        else:
            results.append(("❌", "Load speed is very slow", f"Took {load_time}ms — users will leave"))

        # Check 3: HTTPS
        if url.startswith("https"):
            results.append(("✅", "HTTPS is enabled", "Site uses a secure connection"))
        else:
            results.append(("❌", "No HTTPS", "Site is not secure — data is not encrypted"))

        # Check 4: Title tag
        if "<title>" in html.lower():
            results.append(("✅", "Page has a title tag", "Good for SEO and browser tabs"))
        else:
            results.append(("❌", "No title tag found", "Missing <title> — bad for SEO"))

        # Check 5: Meta description
        if 'name="description"' in html.lower():
            results.append(("✅", "Meta description exists", "Good for search engine previews"))
        else:
            results.append(("⚠️", "No meta description", "Missing meta description — bad for SEO"))

        # Check 6: Mobile friendly
        if "viewport" in html.lower():
            results.append(("✅", "Mobile friendly", "Viewport tag found"))
        else:
            results.append(("⚠️", "May not be mobile friendly", "No viewport meta tag found"))

        # Check 7: Image alt text
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        missing_alt = sum(1 for img in images if "alt=" not in img.lower())
        if missing_alt == 0:
            results.append(("✅", "All images have alt text", "Good for accessibility"))
        else:
            results.append(("⚠️", f"{missing_alt} image(s) missing alt text", "Bad for accessibility and SEO"))

    except requests.exceptions.ConnectionError:
        results.append(("❌", "Cannot connect to site", "Check if the URL is correct"))
    except requests.exceptions.Timeout:
        results.append(("❌", "Site timed out", "No response after 10 seconds"))
    except Exception as e:
        results.append(("❌", "Something went wrong", str(e)))

    return results, url


def make_report(url, results):
    passed  = [r for r in results if r[0] == "✅"]
    warned  = [r for r in results if r[0] == "⚠️"]
    failed  = [r for r in results if r[0] == "❌"]

    report = f"""You are a QA engineer. Write a short professional website quality report.

Website tested: {url}

Test results:
"""
    for icon, name, detail in results:
        status = "PASS" if icon == "✅" else "WARNING" if icon == "⚠️" else "FAIL"
        report += f"- {name}: {status} — {detail}\n"

    report += f"""
Summary: {len(passed)} passed, {len(warned)} warnings, {len(failed)} failed.

Write:
1. A 2-sentence summary of the site's quality
2. The most critical issues to fix
3. Quick wins (easy improvements)
4. Overall score out of 10

Keep it short and clear. Use simple language."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": st.secrets["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": report}]
            },
            timeout=30
        )
        return resp.json()["content"][0]["text"]
    except Exception:
        lines = "\n".join([f"- {n}: {d}" for _, n, d in results])
        return f"**Summary**\n{len(passed)} checks passed, {len(warned)} warnings, {len(failed)} failed.\n\n**Findings**\n{lines}"


if st.button("🚀 Run Check", type="primary", use_container_width=True):
    if not url.strip():
        st.warning("Please enter a URL first.")
    else:
        with st.spinner("Checking website..."):
            results, checked_url = run_checks(url.strip())

        passed = sum(1 for r in results if r[0] == "✅")
        warned = sum(1 for r in results if r[0] == "⚠️")
        failed = sum(1 for r in results if r[0] == "❌")

        st.divider()

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Passed", passed)
        col2.metric("⚠️ Warnings", warned)
        col3.metric("❌ Failed", failed)

        st.subheader("Check Results")
        for icon, name, detail in results:
            if icon == "✅":
                st.success(f"**{name}** — {detail}")
            elif icon == "⚠️":
                st.warning(f"**{name}** — {detail}")
            else:
                st.error(f"**{name}** — {detail}")

        st.divider()
        st.subheader("🤖 AI Quality Report")
        with st.spinner("Generating AI report..."):
            report = make_report(checked_url, results)
        st.markdown(report)

st.divider()
st.caption("Built with Python + Streamlit + Claude AI · By Shivansh Mudgal")
