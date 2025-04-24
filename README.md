# Simple ATS Resume Checker
A simple resume analyzer and job description matcher built with Python and Streamlit to help job seekers optimize their resumes for Applicant Tracking Systems (ATS).

## Features

- Upload resumes in LaTeX (.tex) or PDF format
- Keyword analysis against 70+ tech industry terms
- Resume scoring based on:
  - Section completeness (Experience, Skills, Education)
  - Presence of contact details
  - Length and bullet point usage
  - Readability score
- Flesch Reading Ease Score
- Job description keyword matching with match score
- Visual keyword frequency charts

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/donrami/ats-resume-checker.git
cd ats-resume-checker
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run ats-resume-checker.py
```

## License

This project is licensed under the GPL-2.0 License.
