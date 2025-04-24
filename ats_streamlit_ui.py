import streamlit as st
import re
import requests
from collections import Counter
from pathlib import Path
from pylatexenc.latex2text import LatexNodes2Text
import textstat
import fitz
from langdetect import detect

# List of common tech-related keywords
KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "sql", "nosql",
    "react", "vue", "angular", "svelte", "nextjs", "node", "express", "django", "flask", "spring",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci", "cd",
    "html", "css", "sass", "less", "tailwind", "bootstrap", "graphql", "rest", "api",
    "linux", "unix", "windows", "bash", "powershell",
    "machine learning", "deep learning", "nlp", "computer vision", "data science", "data analysis",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "matplotlib", "seaborn",
    "excel", "tableau", "power bi", "lookml",
    "git", "github", "gitlab", "bitbucket",
    "agile", "scrum", "kanban", "jira", "confluence",
    "communication", "collaboration", "leadership", "mentorship", "problem solving"
]

WEIGHTS = {
    "missing_section": 8,
    "missing_phone": 15,
    "missing_email": 15,
    "few_bullets": 5,
    "too_long": 10
}

SECTION_ALIASES = {
    "experience": ["experience", "work history", "professional background"],
    "education": ["education", "academic background", "studies"],
    "skills": ["skills", "technical skills", "competencies"],
    "projects": ["projects", "portfolio", "case studies"]
}

def extract_text_from_latex(content):
    return LatexNodes2Text().latex_to_text(content)

def extract_text_from_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)

def extract_keywords_from_job_text(text):
    words = re.findall(r"\b\w+\b", text.lower())
    word_counts = Counter(words)
    return {word: count for word, count in word_counts.items() if word in KEYWORDS and count > 0}

def analyze_resume(text):
    tips = []
    positives = []
    score = 100
    lower_text = text.lower()

    for section, variants in SECTION_ALIASES.items():
        if any(variant in lower_text for variant in variants):
            positives.append(f"Found section: '{section.title()}'")
        else:
            tips.append(f"Missing section: '{section.title()}' (-{WEIGHTS['missing_section']} pts)")
            score -= WEIGHTS['missing_section']

    if re.search(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}", text):
        positives.append("Phone number found")
    else:
        tips.append(f"Missing or invalid phone number (-{WEIGHTS['missing_phone']} pts)")
        score -= WEIGHTS['missing_phone']

    if re.search(r"[\w.-]+@[\w.-]+", text):
        positives.append("Email address found")
    else:
        tips.append(f"Missing email address (-{WEIGHTS['missing_email']} pts)")
        score -= WEIGHTS['missing_email']

    if text.count("•") >= 3:
        positives.append("Sufficient bullet points found")
    else:
        tips.append(f"Too few bullet points (-{WEIGHTS['few_bullets']} pts)")
        score -= WEIGHTS['few_bullets']

    word_count = len(text.split())
    if word_count <= 1000:
        positives.append(f"Reasonable length: {word_count} words")
    else:
        tips.append(f"Resume is too long ({word_count} words) (-{WEIGHTS['too_long']} pts)")
        score -= WEIGHTS['too_long']

    words = re.findall(r"\b\w+\b", lower_text)
    word_counts = Counter(words)
    keyword_density = {kw: word_counts.get(kw, 0) for kw in KEYWORDS if word_counts.get(kw, 0) > 0}

    readability_score = textstat.flesch_reading_ease(text)

    return tips, positives, score, keyword_density, set(word_counts), readability_score

# Streamlit UI
st.title("ATS Resume Checker + Job Match")
resume_file = st.file_uploader("Upload your LaTeX or PDF resume", type=["tex", "pdf"])

job_desc_text = st.text_area("Paste job description text (recommended)", height=150, help="Pasting the job description text directly works better than URLs due to limitations with job boards like LinkedIn.")
submit_job = st.button("Analyze Job Description")

if resume_file is not None:
    if resume_file.name.endswith(".tex"):
        content = resume_file.read().decode("utf-8")
        plain_text = extract_text_from_latex(content)
    elif resume_file.name.endswith(".pdf"):
        plain_text = extract_text_from_pdf(resume_file)

    try:
        detected_language = detect(plain_text)
        if detected_language != "en":
            st.error("❌ Only English language resumes are currently supported. Please upload an English version.")
        else:
            tips, positives, score, keyword_density, resume_words, readability_score = analyze_resume(plain_text)

            st.subheader(f"Score: {score}/100")
            st.metric("📖 Readability (Flesch Ease)", f"{readability_score:.1f}", help="Higher is easier to read. Aim for 60–70+. Calculated using: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)")

            with st.expander("📚 Readability Tips"):
                st.markdown("""
                **How the Flesch Reading Ease Score Works:**

                The formula is:

                `206.835 - 1.015 × (total words / total sentences) - 84.6 × (total syllables / total words)`

                - 📈 Higher scores = easier to read (ideal: 60–70+)
                - 📉 Lower scores = complex sentences or jargon-heavy text

                **Tips to improve readability:**
                - Use shorter sentences
                - Prefer simpler words
                - Avoid long paragraphs
                - Use bullet points when listing things
                - Replace passive voice with active verbs
                """)

            with st.expander("✅ Positive Matches"):
                for p in positives:
                    st.success(p)

            with st.expander("⚠️ Suggestions"):
                for t in tips:
                    st.warning(t)

            if keyword_density:
                st.subheader("📊 Resume Keyword Density")
                st.bar_chart(keyword_density)

            if submit_job:
                job_text = job_desc_text.strip()
                st.subheader("🔍 Job Description Keyword Match")
                if job_text:
                    job_keywords = extract_keywords_from_job_text(job_text)
                    if job_keywords:
                        st.write("**Top Keywords in Job Description:**")
                        st.bar_chart(job_keywords)

                        matched_keywords = set(job_keywords) & resume_words
                        missing_keywords = set(job_keywords) - resume_words
                        match_score = len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0

                        st.metric("🔢 Match Score", f"{match_score:.1f}%")

                        with st.expander("🟡 Missing Keywords from Resume"):
                            for kw in sorted(missing_keywords):
                                st.info(kw)
                    else:
                        st.write("No matching tech keywords found in job description.")
                else:
                    st.info("💡 Add a job description above and click the button to see keyword match analysis.")
    except Exception as e:
        st.error(f"Error processing the file: {e}")

st.markdown("---")
st.markdown("Developed with ❤️ to help your resume beat the bots!")

