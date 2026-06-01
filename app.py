import json
import os
from typing import Any, Optional

import fitz
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-4o-2024-05-13"


SYSTEM_PROMPT = """
You are a careful job application assistant.

Analyze a resume and job description, then return only valid JSON with this shape:
{
  "match_score": {
    "score": 0,
    "explanation": "brief explanation"
  },
  "missing_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5"],
  "red_flags": ["red flag 1", "red flag 2", "red flag 3"],
  "cover_letter": "tailored cover letter",
  "rewritten_experience": "rewritten Experience section"
}

Rules:
- The match score must be an integer from 0 to 100.
- Missing keywords must be important terms from the job description that are absent or weak in the resume.
- Red flags must be issues a hiring manager would notice, such as unclear impact, weak alignment, gaps, vague wording, or missing proof.
- The cover letter must be specific to the job description and grounded in the resume.
- The rewritten Experience section must naturally incorporate the missing keywords where truthful.
- Rewrite every experience bullet using Google's XYZ formula: "Accomplished X as measured by Y by doing Z."
- Bullets must sound natural, human, and credible. Do not invent employers, dates, degrees, certifications, or impossible metrics.
- If exact metrics are missing, use measured outcomes already present in the resume or write impact-focused bullets without fake numbers.
"""


def extract_resume_text(uploaded_file: Any) -> str:
    """Extract plain text from an uploaded PDF resume using PyMuPDF."""
    pdf_bytes = uploaded_file.getvalue()
    resume_text = []

    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        for page in document:
            resume_text.append(page.get_text())

    return "\n".join(resume_text).strip()


def get_openrouter_client() -> Optional[OpenAI]:
    """Create an OpenRouter client if the API key is available."""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "http://127.0.0.1:8501",
            "X-Title": "Job Application Assistant",
        },
    )


def analyze_application(client: OpenAI, resume_text: str, job_description: str) -> dict[str, Any]:
    """Send the resume and job description to OpenRouter and return structured analysis."""
    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Resume text:\n"
                    f"{resume_text}\n\n"
                    "Job description:\n"
                    f"{job_description}"
                ),
            },
        ],
        temperature=0.4,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenRouter returned an empty response.")

    return json.loads(content)


def show_analysis(analysis: dict[str, Any]) -> None:
    """Render the five requested analysis sections."""
    match_score = analysis.get("match_score", {})
    score = match_score.get("score", "N/A")
    explanation = match_score.get("explanation", "")

    st.header("Match Score")
    st.metric("Score", f"{score}/100")
    st.write(explanation)

    st.header("Top 5 Missing Keywords")
    missing_keywords = analysis.get("missing_keywords", [])
    for keyword in missing_keywords[:5]:
        st.write(f"- {keyword}")

    st.header("Top 3 Red Flags")
    red_flags = analysis.get("red_flags", [])
    for red_flag in red_flags[:3]:
        st.write(f"- {red_flag}")

    st.header("Tailored Cover Letter")
    st.write(analysis.get("cover_letter", ""))

    st.header("Rewritten Experience Section")
    st.text_area(
        "Copy and paste this into your resume:",
        value=analysis.get("rewritten_experience", ""),
        height=350,
    )


def main() -> None:
    st.set_page_config(page_title="Job Application Assistant", layout="centered")

    st.title("Job Application Assistant")
    st.write("Upload your resume and paste a job description to get a tailored application review.")

    resume_file = st.file_uploader("Resume PDF", type=["pdf"])
    job_description = st.text_area("Job Description", height=260)

    if st.button("Analyze", type="primary"):
        client = get_openrouter_client()

        if client is None:
            st.error("Missing OPENROUTER_API_KEY. Add it to a .env file and restart the app.")
            return

        if resume_file is None:
            st.error("Please upload your resume as a PDF.")
            return

        if not job_description.strip():
            st.error("Please paste a job description.")
            return

        try:
            with st.spinner("Analyzing your resume and job description..."):
                resume_text = extract_resume_text(resume_file)

                if not resume_text:
                    st.error("No text could be extracted from the PDF. Try a text-based resume PDF.")
                    return

                analysis = analyze_application(client, resume_text, job_description.strip())

            show_analysis(analysis)

        except json.JSONDecodeError:
            st.error("The analysis response could not be read. Please try again.")
        except Exception as error:
            st.error(f"Something went wrong: {error}")


if __name__ == "__main__":
    main()
