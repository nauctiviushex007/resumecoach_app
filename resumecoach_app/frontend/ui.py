"""Presentation layer for ResumeCoach. Analysis and AI logic live in backend/."""

import hashlib
import streamlit as st

from backend.analysis import analyze
from backend.ai import rewrite_bullet, write_cover_letter
from backend.files import read_file


CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #f4f5ff;
    --muted: #a6abc5;
    --violet: #9b8cff;
    --cyan: #6bdcf2;
    --panel: rgba(22, 26, 53, .78);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            ellipse at 8% 0%,
            rgba(106, 76, 255, .20),
            transparent 35%
        ),
        radial-gradient(
            ellipse at 95% 18%,
            rgba(40, 190, 220, .12),
            transparent 30%
        ),
        #090d1c;
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: rgba(9, 13, 28, .72);
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent;
}

.block-container {
    max-width: 1240px;
    padding-top: 2.2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #11162d 0%,
        #0c1122 100%
    );
    border-right: 1px solid rgba(161, 155, 255, .14);
}

[data-testid="stSidebar"] * {
    color: #e9eaff;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #b7bdd7;
}

[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(112, 124, 190, .12);
    border: 1px solid rgba(148, 155, 220, .2);
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -.035em;
    color: #f5f5ff;
}

h2 {
    font-size: 1.55rem !important;
}

h3 {
    font-size: 1.13rem !important;
}

p, label, .stCaption {
    color: #b7bdd7;
}

/* Small uppercase section labels */

.eyebrow {
    color: #a99aff;
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: .19em;
    text-transform: uppercase;
    margin-bottom: .7rem;
}

/* Main animated hero section */

.hero {
    position: relative;
    overflow: hidden;
    padding: 2.1rem 2.2rem;
    margin-bottom: 1.55rem;
    border: 1px solid rgba(166, 153, 255, .25);
    border-radius: 25px;
    background: linear-gradient(
        112deg,
        rgba(74, 55, 155, .48),
        rgba(18, 38, 75, .78) 58%,
        rgba(15, 76, 91, .48)
    );
    box-shadow: 0 18px 60px rgba(0, 0, 0, .22);
}

.hero:after {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    right: 5%;
    top: -130px;
    border-radius: 50%;
    background: rgba(124, 220, 255, .17);
    filter: blur(5px);
    animation: floatGlow 7s ease-in-out infinite alternate;
}

.hero h1 {
    font-size: clamp(2.1rem, 4vw, 3.15rem);
    line-height: 1.08;
    margin: 0 0 .65rem;
}

.hero h1 span {
    background: linear-gradient(
        90deg,
        #b7a8ff,
        #76e4f4
    );
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero p {
    max-width: 660px;
    margin: 0;
    color: #d0d3ee;
    font-size: 1rem;
}

.hero-meta {
    display: flex;
    gap: 9px;
    flex-wrap: wrap;
    margin-top: 1.25rem;
}

.pill {
    display: inline-flex;
    padding: 6px 11px;
    border: 1px solid rgba(206, 205, 255, .22);
    border-radius: 999px;
    background: rgba(9, 13, 35, .28);
    color: #e3e4ff;
    font-size: .75rem;
}

@keyframes floatGlow {
    from {
        transform: translate(0, 0) scale(.9);
    }

    to {
        transform: translate(-22px, 24px) scale(1.12);
    }
}

/* Section headings */

.section-kicker {
    color: #9d91ed;
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .15em;
    text-transform: uppercase;
    margin-bottom: .35rem;
}

.section-sub {
    color: #9da5c4;
    margin-top: -.45rem;
    margin-bottom: 1rem;
    font-size: .9rem;
}

/* Glass-style cards */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid rgba(155, 163, 220, .16) !important;
    border-radius: 18px !important;
    background: linear-gradient(
        145deg,
        rgba(26, 32, 65, .78),
        rgba(15, 21, 44, .82)
    );
    box-shadow: 0 10px 35px rgba(0, 0, 0, .12);
}

/* Input fields */

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: rgba(7, 11, 26, .68) !important;
    color: #f2f3ff !important;
    border: 1px solid rgba(151, 161, 218, .25) !important;
    border-radius: 12px !important;
}

textarea:focus,
input:focus {
    border-color: #9d8cff !important;
    box-shadow: 0 0 0 2px rgba(157, 140, 255, .15) !important;
}

/* Resume upload box */

[data-testid="stFileUploader"] section {
    background: rgba(8, 13, 30, .45);
    border: 1px dashed rgba(160, 157, 239, .38);
    border-radius: 13px;
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid rgba(172, 160, 255, .35);
    background: linear-gradient(
        100deg,
        #7560e8,
        #4f9edb
    );
    color: white;
    font-weight: 700;
    min-height: 2.65rem;
    transition:
        transform .18s ease,
        filter .18s ease,
        box-shadow .18s ease;
    box-shadow: 0 7px 20px rgba(87, 88, 205, .18);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.12);
    border-color: #c2b8ff;
    box-shadow: 0 10px 26px rgba(103, 99, 226, .28);
    color: white;
}

.stButton > button:active {
    transform: translateY(0);
}

.stButton > button[kind="secondary"] {
    background: rgba(115, 124, 180, .13);
    border: 1px solid rgba(157, 165, 220, .25);
    box-shadow: none;
}

/* Match score metric cards */

div[data-testid="stMetric"] {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(161, 151, 255, .22);
    border-radius: 16px;
    background: linear-gradient(
        140deg,
        rgba(89, 73, 175, .23),
        rgba(28, 73, 103, .2)
    );
}

div[data-testid="stMetricLabel"] {
    color: #b9bfdd;
}

div[data-testid="stMetricValue"] {
    color: #f6f4ff;
    font-family: 'Manrope', sans-serif;
}

/* Progress bar */

[data-testid="stProgress"] > div > div {
    background: linear-gradient(
        90deg,
        #8b75ff,
        #64d8e9
    );
    border-radius: 99px;
}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid rgba(160, 166, 220, .16);
}

.stTabs [data-baseweb="tab"] {
    background: rgba(30, 36, 72, .45);
    border-radius: 10px 10px 0 0;
    padding: 9px 16px;
    color: #b8bfdf;
}

.stTabs [aria-selected="true"] {
    background: rgba(125, 105, 226, .2) !important;
    color: #fff !important;
}

/* Alerts and separators */

[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: rgba(156, 163, 220, .16);
}

/* Footer */

.footer-note {
    text-align: center;
    color: #707998;
    font-size: .75rem;
    padding: 2rem 0 .5rem;
}

.footer-note span {
    color: #9d8cff;
}

/* Login screen */

.login-wrap {
    padding: 4rem 0 1rem;
    max-width: 650px;
}

.login-title {
    font-size: 2.8rem;
}

.login-title span {
    color: #a99aff;
}

.muted {
    color: #a6abc5;
}

/* Mobile responsive layout */

@media (max-width: 700px) {
    .block-container {
        padding: 1.2rem 1rem;
    }

    .hero {
        padding: 1.5rem;
    }

    .hero h1 {
        font-size: 2.1rem;
    }
}

/* ==========================================
   RESUMECOACH PREMIUM VISUAL UPGRADE
   ========================================== */

/* Animated background */
.stApp {
    position: relative;
    isolation: isolate;
    overflow-x: hidden;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: -35%;
    z-index: 0;
    pointer-events: none;

    background:
        radial-gradient(
            circle at 15% 25%,
            rgba(132, 83, 255, 0.25),
            transparent 24%
        ),
        radial-gradient(
            circle at 80% 30%,
            rgba(34, 211, 238, 0.18),
            transparent 22%
        ),
        radial-gradient(
            circle at 55% 85%,
            rgba(168, 85, 247, 0.18),
            transparent 25%
        );

    background-size: 150% 150%;
    animation: backgroundDrift 18s ease-in-out infinite alternate;
}

.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(150, 160, 255, 0.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(150, 160, 255, 0.025) 1px,
            transparent 1px
        );

    background-size: 45px 45px;
    mask-image: linear-gradient(
        to bottom,
        black,
        transparent 85%
    );
}

/* Keep app content above background */
.stApp > header,
.stApp [data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
}

@keyframes backgroundDrift {
    0% {
        transform: translate3d(-3%, -2%, 0) rotate(0deg) scale(1);
    }

    50% {
        transform: translate3d(3%, 2%, 0) rotate(5deg) scale(1.08);
    }

    100% {
        transform: translate3d(-1%, 4%, 0) rotate(-4deg) scale(1.03);
    }
}

/* Custom brand logo */
.brand-row {
    display: flex;
    align-items: center;
    gap: 13px;
    margin-bottom: 22px;
}

.brand-logo {
    width: 49px;
    height: 49px;
    flex-shrink: 0;
    display: grid;
    place-items: center;
    border-radius: 15px;

    background: linear-gradient(
        135deg,
        #9b78ff,
        #6555dc 55%,
        #35c9e8
    );

    box-shadow:
        0 0 20px rgba(139, 92, 246, 0.38),
        inset 0 1px 1px rgba(255,255,255,.35);

    animation: logoFloat 4s ease-in-out infinite;
}

.brand-logo svg {
    width: 29px;
    height: 29px;
}

.brand-name {
    color: #f7f5ff;
    font-family: 'Manrope', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.brand-tagline {
    color: #a9afd0;
    font-size: .68rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 2px;
}

@keyframes logoFloat {
    0%, 100% {
        transform: translateY(0);
        box-shadow: 0 0 18px rgba(139,92,246,.3);
    }

    50% {
        transform: translateY(-4px);
        box-shadow: 0 0 28px rgba(139,92,246,.55);
    }
}

/* Premium hero section */
.hero {
    border: 1px solid rgba(177, 160, 255, .32);
    background:
        radial-gradient(
            circle at 90% 10%,
            rgba(97, 218, 255, .16),
            transparent 30%
        ),
        linear-gradient(
            115deg,
            rgba(65, 48, 140, .72),
            rgba(17, 31, 68, .88) 60%,
            rgba(12, 76, 91, .55)
        );

    box-shadow:
        0 20px 70px rgba(0, 0, 0, .25),
        0 0 35px rgba(117, 92, 255, .10);

    backdrop-filter: blur(18px);
    animation: heroAppear .8s ease-out both;
}

@keyframes heroAppear {
    from {
        opacity: 0;
        transform: translateY(16px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero h1 {
    text-shadow: 0 5px 25px rgba(0,0,0,.18);
}

.hero .brand-row {
    margin-bottom: 26px;
}

/* Premium cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    backdrop-filter: blur(14px);
    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    border-color: rgba(163, 145, 255, .38) !important;
    box-shadow: 0 15px 40px rgba(0, 0, 0, .2);
}

/* Better button glow */
.stButton > button[kind="primary"] {
    background: linear-gradient(
        100deg,
        #8065f5,
        #557de8,
        #38b9d7
    );
    background-size: 200% 200%;
    animation: buttonShimmer 5s ease infinite;
}

@keyframes buttonShimmer {
    0%, 100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

/* Cleaner scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #0b1022;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(#8d75ff, #39bfd9);
    border-radius: 20px;
}

/* Respect reduced-motion settings */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}


</style>
"""



def load_styles():
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Reference-inspired full-page layout */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    .block-container {
        max-width: 1050px !important;
        padding-top: 1.2rem !important;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 5% 15%, rgba(105,75,255,.30), transparent 35%),
            radial-gradient(ellipse at 95% 75%, rgba(0,190,230,.22), transparent 35%),
            linear-gradient(135deg,#09091c,#16082d,#090d20) !important;
        color: #f5f3ff;
    }

    .topbar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:12px 22px;
        margin-bottom:28px;
        background:rgba(9,10,27,.88);
        border:1px solid rgba(160,140,255,.15);
        border-radius:14px;
    }

    .topbrand {
        color:#b49aff;
        font-size:19px;
        font-weight:800;
        letter-spacing:.04em;
    }

    .topbrand span {
        color:#f5f3ff;
    }

    .topnav a {
        color:#c6c5dc;
        text-decoration:none;
        margin-left:25px;
        font-size:14px;
        font-weight:600;
    }

    .upload-heading {
        font-size:30px;
        font-weight:800;
        color:#f7f5ff;
        margin-bottom:8px;
    }

    .upload-description {
        color:#a9a9c5;
        margin-bottom:24px;
    }

    .upload-panel {
        background:rgba(32,16,65,.50);
        border:1px dashed rgba(160,125,255,.8);
        border-radius:24px;
        padding:24px;
        box-shadow:0 0 35px rgba(117,70,255,.13);
    }

    [data-testid="stFileUploader"] section {
        background:rgba(20,13,48,.5) !important;
        border:1px dashed rgba(160,125,255,.7) !important;
        border-radius:18px !important;
        padding:24px !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background:rgba(35,24,65,.72) !important;
        border:1px solid rgba(164,135,255,.20) !important;
        border-radius:20px !important;
    }

    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextArea"] textarea {
        background:rgba(12,12,35,.8) !important;
        border-radius:12px !important;
    }

    .stButton > button {
        border-radius:12px !important;
        min-height:45px;
    }

    @media(max-width:700px) {
        .upload-heading { font-size:24px; }
        .block-container { padding:1rem !important; }
        .topnav a { margin-left:8px; }
    }
    </style>
    """, unsafe_allow_html=True)



def init_state():
    defaults = {
        "analysis": None,
        "sugg": {},
        "final": {},
        "resume": "",
        "job": "",
        "letter": "",
        "loaded": None,
        "letter_box": "",
        "candidate_name": "",
        "company_name": "",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)







def header(asker):
    html = (
        '<div style="display:flex;align-items:center;'
        'justify-content:space-between;padding:18px 25px;'
        'margin-bottom:28px;background:rgba(9,10,27,0.92);'
        'border:1px solid rgba(160,140,255,0.18);'
        'border-radius:15px;">'
        '<div style="color:#b49aff;font-size:21px;font-weight:800;">'
        '✦ ResumeCoach</div>'
        '<div style="display:flex;gap:25px;">'
        '<a href="#upload" style="color:#ffffff;'
        'text-decoration:none;font-weight:600;">Upload</a>'
        '<a href="#dashboard" style="color:#c6b5ff;'
        'text-decoration:none;font-weight:600;">Dashboard</a>'
        '</div></div>'
    )

    st.markdown(html, unsafe_allow_html=True)





def sidebar(asker):
    with st.sidebar:
        st.markdown(
            "<div class='eyebrow'>✦ RESUMECOACH</div>",
            unsafe_allow_html=True,
        )

        st.title("Your workspace")

        st.caption(
            "A little progress today can open a new door tomorrow."
        )

        st.divider()

        st.markdown("**AI assistant**")

        if asker.enabled:
            st.success("AI rewriting is ready")

            st.caption(
                f"Session usage: {asker.calls} / {asker.max_calls} calls"
            )

            st.progress(
                min(asker.calls / asker.max_calls, 1.0)
            )
        else:
            st.info(
                "AI rewriting is off. Resume analysis and manual coaching still work."
            )

        st.divider()

        st.markdown("**Your privacy matters**")

        st.caption(
            "When AI is enabled, the resume and job text needed for a "
            "request are sent to the AI provider. Avoid sharing information "
            "you do not want processed."
        )

        st.markdown(
            """
            <div class='section-kicker'>QUICK WORKFLOW</div>
            1. Add your resume

            2. Paste the job description

            3. Review your match

            4. Approve edits you like
            """,
            unsafe_allow_html=True,
        )



def inputs():
    import hashlib

    st.markdown(
        '<div id="upload"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="upload-heading">📄 Upload Your Resume</div>'
        '<div class="upload-description">'
        'Upload your PDF, DOCX or TXT resume and select your target role '
        'to receive a complete AI analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    # Large resume upload panel
    with st.container(border=True):
        st.markdown(
            "<h3 style='text-align:center;color:#c5a9ff'>"
            "📄 Drag & Drop your resume here</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center;color:#aaa5c8'>"
            "Choose a file from your computer to get started"
            "</p>",
            unsafe_allow_html=True
        )

        up = st.file_uploader(
            "Upload your resume (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            key="resume_upload"
        )

        if up:
            fingerprint = hashlib.sha256(
                up.getvalue()
            ).hexdigest()

            if st.session_state.loaded != fingerprint:
                try:
                    st.session_state.resume = read_file(
                        up.name,
                        up.getvalue()
                    )
                    st.session_state.loaded = fingerprint
                    st.success(f"Resume uploaded: {up.name}")
                except Exception as exc:
                    st.error(f"Unable to read resume: {exc}")

    # Optional manual resume text
    with st.expander("Or paste your resume text manually"):
        st.text_area(
            "Resume text",
            key="resume",
            height=200,
            placeholder="Paste your resume text here..."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Target job role panel
    with st.container(border=True):
        st.markdown(
            "### 🎯 Target Job Role"
        )

        st.caption(
            "Select the role you're applying for to get tailored skill-gap analysis."
        )

        roles = [
            "Software Engineer",
            "Python Developer",
            "Java Developer",
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer",
            "Data Analyst",
            "Data Scientist",
            "Machine Learning Engineer",
            "AI Engineer",
            "Web Developer",
            "Other"
        ]

        role = st.selectbox(
            "Job Role",
            roles,
            key="target_role"
        )

        if role == "Other":
            role = st.text_input(
                "Enter your target role",
                key="custom_target_role"
            )

        st.text_area(
            "Job Description",
            key="job",
            height=190,
            placeholder=(
                "Paste the job description here. Include "
                "responsibilities, skills and qualifications..."
            )
        )

        st.caption(
            "Your resume is not changed automatically. "
            "You approve every suggested edit."
        )

        analyse_clicked = st.button(
            "✦ Analyse My Resume",
            type="primary",
            use_container_width=True
        )

    if analyse_clicked:
        if len(st.session_state.resume.strip()) < 30:
            st.error("Please upload or paste your resume first.")

        elif len(st.session_state.job.strip()) < 30:
            st.error("Please enter a job description.")

        else:
            with st.spinner("Analysing your resume..."):
                st.session_state.analysis = analyze(
                    st.session_state.resume,
                    st.session_state.job
                )

                st.session_state.sugg = {}
                st.session_state.final = {}
                st.session_state.letter = ""

            st.success("Your resume analysis is ready!")
            st.rerun()



def empty_state():
    st.markdown(
        """
        <div style="
            text-align:center;
            padding:1.5rem 1rem 2.2rem;
            color:#a6abc5;
        ">
          <div style="
              font-size:2rem;
              margin-bottom:.5rem;
          ">✧</div>

          <div style="
              font-family:Manrope;
              font-size:1.1rem;
              color:#e6e7ff;
              font-weight:700;
          ">
              Your career story starts here
          </div>

          <div style="
              font-size:.9rem;
              margin-top:.35rem;
          ">
              Add your resume and a job description above
              to unlock your personalised insights.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def results():
    st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)
    a = st.session_state.analysis

    st.markdown(
        '<div class="section-kicker">02 / YOUR INSIGHTS</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Your resume match")

    st.markdown(
        """
        <p class="section-sub">
            A practical keyword comparison and a few checks
            to help you strengthen your application.
        </p>
        """,
        unsafe_allow_html=True,
    )

    score = a["score"]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Keyword match",
            f"{score}%" if score is not None else "—",
            help=(
                "Keyword overlap only. This is not an employer ATS score."
            ),
        )

    with c2:
        st.metric(
            "Keywords found",
            len(a["matched"]),
        )

    with c3:
        st.metric(
            "Keywords to review",
            len(a["missing"]),
        )

    if score is not None:
        st.progress(
            score / 100,
            text=f"{score}% keyword overlap",
        )

    st.caption(
        "This is a simple keyword comparison, not a prediction of "
        "an employer's ATS result or hiring decision."
    )

    matched_col, missing_col = st.columns(2, gap="large")

    with matched_col:
        with st.container(border=True):
            st.markdown(
                "### <span style='color:#70d8ae'>✓</span> "
                "Already in your resume",
                unsafe_allow_html=True,
            )

            if a["matched"]:
                st.markdown(
                    " ".join(
                        f"`{word}`"
                        for word in a["matched"]
                    )
                )
            else:
                st.caption("No matching keywords found yet.")

    with missing_col:
        with st.container(border=True):
            st.markdown(
                "### <span style='color:#f0bd78'>＋</span> "
                "Worth reviewing",
                unsafe_allow_html=True,
            )

            if a["missing"]:
                st.markdown(
                    " ".join(
                        f"`{word}`"
                        for word in a["missing"]
                    )
                )
            else:
                st.caption(
                    "Great — all extracted keywords were found in your resume."
                )

            st.caption(
                "Only add a keyword if it accurately describes your experience."
            )

    with st.container(border=True):
        st.markdown("### Resume quality checklist")

        for label, ok in a["checks"]:
            icon = "🟢" if ok else "🟠"
            st.markdown(f"{icon} &nbsp; {label}")


def _improve(i, asker):
    a = st.session_state.analysis

    suggestion = rewrite_bullet(
        asker,
        a["bullets"][i],
        st.session_state.job,
        a["missing"],
    )

    if suggestion["text"]:
        st.session_state[f"edit{i}"] = suggestion["text"]

    st.session_state.sugg[i] = suggestion


def _accept(i):
    st.session_state.final[i] = st.session_state[f"edit{i}"]


def coach(asker):
    a = st.session_state.analysis

    st.markdown(
        '<div class="section-kicker">03 / POLISH YOUR STORY</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Bullet point coach")

    st.markdown(
        """
        <p class="section-sub">
            Make your achievements clearer and more impactful.
            Review every suggestion before accepting it.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not a["bullets"]:
        st.info(
            "No bullet points were detected. Start achievement lines "
            "with - or •, then analyse again."
        )
        return

    for i, bullet in enumerate(a["bullets"]):
        with st.container(border=True):
            top, button_col = st.columns([4, 1])

            with top:
                st.caption(
                    f"EXPERIENCE BULLET {i + 1:02d}"
                )
                st.write(bullet)

            with button_col:
                st.button(
                    "✦ Improve",
                    key=f"imp{i}",
                    on_click=_improve,
                    args=(i, asker),
                    use_container_width=True,
                )

            suggestion = st.session_state.sugg.get(i)

            if suggestion and suggestion["text"]:
                st.text_area(
                    "Edit the suggested version",
                    key=f"edit{i}",
                    height=100,
                )

                for warning in suggestion["warn"]:
                    st.warning(warning)

                accepted_col, status_col = st.columns([1, 3])

                with accepted_col:
                    st.button(
                        "Accept change",
                        key=f"acc{i}",
                        on_click=_accept,
                        args=(i,),
                        use_container_width=True,
                    )

                with status_col:
                    if i in st.session_state.final:
                        st.success(
                            "Approved — included in your final copy."
                        )

            elif suggestion:
                st.info(
                    suggestion["hint"]
                    + (
                        " Add an API key to enable AI rewrites."
                        if not asker.enabled
                        else " Try again when your AI call limit resets."
                    )
                )

    st.markdown("#### Your approved bullets")

    approved = "\n".join(
        "• " + st.session_state.final.get(i, bullet)
        for i, bullet in enumerate(a["bullets"])
    )

    st.code(approved, language=None)

    st.download_button(
        "Download improved bullets",
        approved,
        file_name="improved_resume_bullets.txt",
        mime="text/plain",
    )


def letter(asker):
    st.markdown(
        '<div class="section-kicker">04 / MAKE YOUR INTRODUCTION</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Cover letter studio")

    st.markdown(
        """
        <p class="section-sub">
            Create a first draft, then make it sound like you.
            Keep every detail accurate.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        name_col, company_col = st.columns(2)

        with name_col:
            name = st.text_input(
                "Your name",
                key="candidate_name",
                placeholder="e.g. Alex Morgan",
            )

        with company_col:
            company = st.text_input(
                "Company",
                key="company_name",
                placeholder="e.g. Acme Technologies",
            )

        if st.button(
            "✦ Draft my cover letter",
            type="primary",
        ):
            with st.spinner("Preparing your cover letter..."):
                st.session_state.letter = write_cover_letter(
                    asker,
                    st.session_state.resume,
                    st.session_state.job,
                    name,
                    company,
                )

                st.session_state.letter_box = st.session_state.letter

        if st.session_state.letter:
            st.text_area(
                "Your editable draft",
                key="letter_box",
                height=280,
            )

            st.download_button(
                "Download cover letter",
                st.session_state.letter_box,
                file_name="cover_letter.txt",
                mime="text/plain",
            )
            
def visual_fix():
    import streamlit as st

    st.markdown("""
    <style>
    /* Animated page background */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 15% 20%, rgba(0, 210, 255, 0.15), transparent 40%),
            radial-gradient(ellipse at 85% 75%, rgba(130, 70, 255, 0.18), transparent 40%),
            linear-gradient(135deg, #070b18, #10152b, #080d1c);
        background-size: 200% 200%;
        animation: resumeGradient 12s ease infinite;
    }

    @keyframes resumeGradient {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Keep the main page transparent so the background shows */
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Improve the main content appearance */
    [data-testid="stMainBlockContainer"] {
        position: relative;
        z-index: 1;
    }

    /* Smooth buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(0, 210, 255, 0.5);
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 18px rgba(0, 210, 255, 0.35);
        border-color: #00d2ff;
    }

    /* Rounded upload area */
    [data-testid="stFileUploader"] {
        border-radius: 16px;
    }

    @media (prefers-reduced-motion: reduce) {
        [data-testid="stAppViewContainer"] {
            animation: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)
