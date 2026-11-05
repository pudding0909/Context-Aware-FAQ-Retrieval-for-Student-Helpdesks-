import html

import streamlit as st

import pandas as pd

import io

import re

import streamlit.components.v1 as components

from faq_engine import FAQEngine



st.set_page_config(page_title="CampusConnect | Student Helpdesk", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")



st.markdown("""

<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }

.stApp { background:linear-gradient(180deg,#f7f9ff 0%,#f8fafc 45%,#f1f5f9 100%); }

.block-container { max-width:1180px; padding-top:1.6rem; padding-bottom:3rem; }

section[data-testid="stSidebar"] { background:#101c3b !important; }

section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color:#fff !important; -webkit-text-fill-color:#fff !important; }

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#dbeafe !important; -webkit-text-fill-color:#dbeafe !important; }

section[data-testid="stSidebar"] [data-testid="stButton"] > button { background:#fff !important; background-color:#fff !important; border:1px solid #bfdbfe !important; border-radius:12px !important; min-height:48px !important; padding:10px 12px !important; width:100% !important; opacity:1 !important; box-shadow:none !important; }

section[data-testid="stSidebar"] [data-testid="stButton"] > button, section[data-testid="stSidebar"] [data-testid="stButton"] > button *, section[data-testid="stSidebar"] [data-testid="stButton"] > button p, section[data-testid="stSidebar"] [data-testid="stButton"] > button span, section[data-testid="stSidebar"] [data-testid="stButton"] > button div { color:#172554 !important; -webkit-text-fill-color:#172554 !important; opacity:1 !important; visibility:visible !important; font-weight:600 !important; }

section[data-testid="stSidebar"] [data-testid="stButton"] > button:hover { background:#dbeafe !important; border-color:#60a5fa !important; }

.hero { position:relative; overflow:hidden; padding:2.2rem 2.4rem; border-radius:25px; color:white; background:linear-gradient(120deg,#172554 0%,#2546a8 58%,#0f766e 120%); box-shadow:0 18px 45px rgba(37,70,168,.18); margin-bottom:1.35rem; }

.hero:after { content:'✦'; position:absolute; right:7%; top:-55px; font-size:220px; color:rgba(255,255,255,.07); pointer-events:none; }

.eyebrow { font-size:.76rem; text-transform:uppercase; letter-spacing:.16em; font-weight:700; color:#bfdbfe; margin-bottom:.65rem; }

.hero h1 { font-family:'Manrope',sans-serif; color:#fff !important; -webkit-text-fill-color:#fff !important; font-size:clamp(2rem,4vw,3.1rem); font-weight:800; line-height:1.12; margin:0 0 .7rem 0; }

.hero p { color:#e0e7ff; font-size:1.03rem; margin:0; max-width:680px; }

.pill { display:inline-block; border:1px solid rgba(255,255,255,.25); border-radius:99px; padding:.35rem .7rem; margin-top:1.1rem; font-size:.78rem; color:#f8fafc; background:rgba(255,255,255,.1); }

.section-title { font-family:'Manrope',sans-serif; font-size:1.18rem; font-weight:800; color:#172554; margin:.4rem 0 .25rem 0; }

.subtext { color:#64748b; font-size:.92rem; margin-bottom:.9rem; }

.panel { background:white; border:1px solid #e2e8f0; border-radius:19px; padding:1.25rem 1.35rem; box-shadow:0 6px 22px rgba(15,23,42,.035); }

.answer-panel { background:linear-gradient(135deg,#eff6ff,#f0fdfa); border:1px solid #93c5fd; border-radius:18px; padding:1.3rem 1.4rem; color:#172554; line-height:1.85; font-size:1.04rem; box-shadow:0 8px 25px rgba(37,99,235,.08); scroll-margin-top:25px; overflow-wrap:anywhere; }

.result-card { background:#fff; border:1px solid #e2e8f0; border-radius:15px; padding:1rem 1.1rem; margin:.55rem 0; }

.result-title { color:#1e293b; font-weight:700; font-size:1rem; }

.meta { color:#64748b; font-size:.82rem; margin-top:.45rem; }

div.stButton > button, div[data-testid="stFormSubmitButton"] button { border-radius:12px; font-weight:700; min-height:2.8rem; }

div[data-testid="stForm"] { background:white; padding:1.15rem 1.2rem .75rem; border:1px solid #e2e8f0; border-radius:18px; box-shadow:0 8px 28px rgba(15,23,42,.04); }

[data-testid="stMetric"] { background:white; padding:.9rem 1rem; border:1px solid #e2e8f0; border-radius:15px; }

footer {visibility:hidden;}

@media (max-width:768px) { .hero {padding:1.5rem;} .hero h1 {font-size:2rem;} }

</style>

""", unsafe_allow_html=True)



if "question" not in st.session_state:

    st.session_state.question = ""

if "run_search" not in st.session_state:

    st.session_state.run_search = False

if "history" not in st.session_state:

    st.session_state.history = []



suggestions = [

    "How can I download my hall ticket?",

    "How do I check my attendance?",

    "How can I apply for revaluation?",

    "I lost my student ID card",

    "Where can I check my semester results?",

]



with st.sidebar:

    st.markdown("<div style='font-size:2rem'>🎓</div><h2 style='margin:.1rem 0;color:white'>CampusConnect</h2><p style='font-size:.88rem;color:#dbeafe'>Student support, made simpler.</p>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 💡 Try asking")

    for index, suggestion in enumerate(suggestions):

        if st.button(suggestion, key=f"suggestion_{index}", use_container_width=True):

            st.session_state.question = suggestion

            st.session_state.run_search = True

            st.rerun()

    st.markdown("---")





st.markdown("""

<div class="hero">

  <div class="eyebrow">YOUR CAMPUS, ONE QUESTION AWAY</div>

  <h1>How can we help you today?</h1>

  <p>Find answers about exams, attendance, student ID cards, results, fees and common college procedures.</p>



</div>

""", unsafe_allow_html=True)



@st.cache_resource(show_spinner="Loading the FAQ dataset and search engine…")

def load_engine():

    return FAQEngine(threshold=0.42)



try:

    engine = load_engine()

except Exception as exc:

    st.error("The FAQ engine could not be loaded. Check that data/faq_dataset_1.csv, data/faq_dataset_2.csv and data/faq_dataset_3.csv exist and the required packages are installed.")

    st.exception(exc)

    st.stop()



col_main, col_side = st.columns([1.75, 1], gap="large")

with col_main:

    st.markdown('<div class="section-title">🔎 Ask the helpdesk</div><div class="subtext">Type questions, upload a questions file or document, extract questions from an image, or use voice input.</div>', unsafe_allow_html=True)

    st.caption("You can type several questions (one per line), upload TXT/CSV/PDF/DOCX files, upload an image (PNG/JPG) containing questions, or record a voice question. Extracted text is shown before searching.")

    with st.form("faq_question_form", clear_on_submit=False):

        query_text = st.text_area("Your questions", value=st.session_state.question, height=150, placeholder="How do I download my hall ticket?\nHow can I check attendance?\nHow do I apply for revaluation?")

        question_file = st.file_uploader("Upload questions or a document (TXT, CSV, PDF, DOCX, PNG, JPG)", type=["txt", "csv", "pdf", "docx", "png", "jpg", "jpeg"])

        voice_audio = st.audio_input("Or record a question (optional)")

        voice_file = st.file_uploader("Or upload recorded audio (WAV, optional)", type=["wav"], key="voice_file")

        submitted = st.form_submit_button("✨ Find answers", type="primary", use_container_width=True)



with col_side:

    st.markdown('<div class="panel"><div class="section-title">🧭 What can I ask?</div><p class="subtext" style="margin-bottom:.5rem">Explore common student services</p></div>', unsafe_allow_html=True)

    categories = [

        ("📝", "Examinations", "Hall tickets, exam schedules"),

        ("📊", "Attendance", "Attendance percentage, eligibility"),

        ("🎓", "Results & grades", "Semester results, revaluation"),

        ("🪪", "Student services", "ID cards, certificates"),

        ("💳", "Fees & payments", "Receipts, payment issues"),

    ]

    for icon, title, description in categories:

        st.markdown(f'<div class="result-card"><div class="result-title">{icon} &nbsp;{html.escape(title)}</div><div class="meta">{html.escape(description)}</div></div>', unsafe_allow_html=True)



should_search = submitted or st.session_state.run_search

if should_search:

    st.session_state.run_search = False

    questions = []

    if submitted and question_file is not None:

        try:

            filename = question_file.name.lower()

            raw = question_file.getvalue()

            if filename.endswith(".txt"):

                uploaded_text = raw.decode("utf-8-sig")

                questions.extend([line.strip().lstrip("-•0123456789.) ").strip() for line in uploaded_text.splitlines() if line.strip()])

            elif filename.endswith(".csv"):

                uploaded_df = pd.read_csv(io.BytesIO(raw)).fillna("")

                candidate = next((col for col in uploaded_df.columns if col.strip().lower() in {"question", "query", "questions"}), None)

                if candidate is None:

                    st.error("CSV needs a column named question, query, or questions.")

                    st.stop()

                questions.extend(uploaded_df[candidate].astype(str).str.strip().tolist())

            elif filename.endswith(".pdf"):

                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(raw))

                extracted = "\n".join(page.extract_text() or "" for page in reader.pages)

                questions.extend([line.strip().lstrip("-•0123456789.) ").strip() for line in extracted.splitlines() if line.strip()])

            elif filename.endswith(".docx"):

                from docx import Document

                doc = Document(io.BytesIO(raw))

                extracted = "\n".join(paragraph.text for paragraph in doc.paragraphs)

                questions.extend([line.strip().lstrip("-•0123456789.) ").strip() for line in extracted.splitlines() if line.strip()])

            elif filename.endswith((".png", ".jpg", ".jpeg")):

                from PIL import Image

                import pytesseract

                image = Image.open(io.BytesIO(raw))

                extracted = pytesseract.image_to_string(image)

                st.info("Text extracted from the image (OCR). Check the text and edit the questions above if needed.")

                st.text_area("OCR text preview", value=extracted, height=120, key="ocr_preview")

                questions.extend([line.strip().lstrip("-•0123456789.) ").strip() for line in extracted.splitlines() if line.strip()])

        except ImportError as exc:

            st.error(f"A package needed for this file type is missing: {exc}. Install all packages from requirements.txt.")

            st.stop()

        except Exception as exc:

            st.error(f"Could not read the uploaded file: {exc}")

            st.stop()

    if submitted and (voice_audio is not None or voice_file is not None):

        try:

            import speech_recognition as sr

            audio_bytes = voice_audio.getvalue() if voice_audio is not None else voice_file.getvalue()

            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:

                audio_data = sr.Recognizer().record(source)

            spoken_text = sr.Recognizer().recognize_google(audio_data)

            st.info(f"Voice transcription: {spoken_text}")

            questions.extend([line.strip() for line in re.split(r"[?**\n**]+", spoken_text) if line.strip()])

        except ImportError:

            st.error("Voice input needs SpeechRecognition and PyAudio. Install the requirements listed in README.md.")

        except Exception as exc:

            st.warning(f"Could not transcribe audio. Try a clear WAV recording or type the question. Details: {exc}")

    if submitted and query_text.strip():

        questions.extend([line.strip().lstrip("-•0123456789.) ").strip() for line in query_text.splitlines() if line.strip()])

    if not submitted and st.session_state.question.strip():

        questions.append(st.session_state.question.strip())

    questions = list(dict.fromkeys(q for q in questions if q))

    if not questions:

        st.warning("Enter one or more questions, or upload a TXT/CSV file.")

    else:

        st.markdown("---")

        st.markdown('<div id="answer-section" class="section-title">💬 Answers</div>', unsafe_allow_html=True)

        st.success(f"Processing {len(questions)} question(s) against {len(engine.faqs):,} FAQ entries across {len(engine.dataset_paths)} datasets.")

        progress = st.progress(0)

        for index, question in enumerate(questions, start=1):

            try:

                result = engine.ask(question, top_k=3)

            except Exception as exc:

                st.error(f"Search failed for: {question}")

                st.exception(exc)

                continue

            with st.container(border=True):

                st.markdown(f"### {index}. {html.escape(question)}")

                if result.get("found"):

                    st.markdown(f'<div class="answer-panel">{html.escape(str(result.get("message", "")))}</div>', unsafe_allow_html=True)

                else:

                    st.warning(result.get("message", "No suitable answer found. Please contact the relevant college office."))

                if result.get("best_score") is not None:

                    st.caption(f"Best similarity: {result['best_score']:.3f} · FAQ ID: {result['results'][0]['faq_id']}")

                with st.expander("See other close matches"):

                    for position, item in enumerate(result.get("results", []), start=1):

                        st.markdown(f"**{position}. {html.escape(item['question'])}** · Similarity {item['score']:.3f}")

                        st.write(item["answer"])

                st.session_state.history.insert(0, {"query": question, "answer": result.get("message", ""), "score": result.get("best_score")})

            progress.progress(index / len(questions))

        st.session_state.history = st.session_state.history[:10]



if st.session_state.history:

    with st.expander("🕘 Recent questions", expanded=False):

        for item in st.session_state.history:

            st.markdown(f'**{html.escape(item["query"])}**')

            st.caption(f'Similarity: {item["score"]:.3f}' if item["score"] is not None else "No similarity score")

            st.write(item["answer"])

            st.divider()



st.markdown("---")


