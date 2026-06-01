# Job Application Assistant

A clean Streamlit web app that helps tailor a resume to a specific job posting.

The user uploads a resume as a PDF, pastes a job description, and clicks **Analyze**. The app extracts text from the resume with PyMuPDF, sends the resume and job description to OpenRouter using GPT-4o by default, and returns a structured application review.

## What It Does

The app returns five sections:

1. **Match Score**  
   A score out of 100 with a short explanation of how well the resume fits the job.

2. **Top 5 Missing Keywords**  
   Important job description keywords that are absent or weak in the resume.

3. **Top 3 Red Flags**  
   Issues a hiring manager might notice, such as vague impact, missing proof, or weak alignment.

4. **Tailored Cover Letter**  
   A cover letter written specifically for the pasted job description and uploaded resume.

5. **Rewritten Experience Section**  
   A copyable rewritten Experience section that naturally includes missing keywords, reduces red flags, and rewrites bullets using Google's XYZ formula:

   > Accomplished X as measured by Y by doing Z.

## Project Files

```text
.
+-- app.py
+-- requirements.txt
+-- README.md
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenRouter API key

Create a `.env` file in the project folder:

```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-2024-05-13
```

You can change `OPENROUTER_MODEL` to another OpenRouter model ID if you want to use a different model.

## Run the App

```bash
streamlit run app.py
```

Streamlit will open the app in your browser. If it does not open automatically, copy the local URL from the terminal and paste it into your browser.

## Screenshot

Add a screenshot of the app here:

```text
[Screenshot placeholder]
```

## Notes

- The resume must be uploaded as a PDF.
- The app works best with text-based PDFs rather than scanned image PDFs.
- The rewritten bullets are instructed to stay truthful and avoid inventing employers, dates, credentials, or unrealistic metrics.
