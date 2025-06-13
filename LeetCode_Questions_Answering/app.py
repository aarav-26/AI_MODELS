import os
import re
import string
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load theories
def load_theories(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        theories = re.split(r'-{10,}', content)
    return theories

def extract_question_title(theory_text):
    match = re.search(r'QUESTION \d+: (.+)', theory_text)
    if match:
        return match.group(1)
    return None

def slugify(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return text.replace(' ', '-')

def get_answer_file(slug, answers_dir):
    files = os.listdir(answers_dir)
    for file in files:
        if file.startswith(slug):
            with open(os.path.join(answers_dir, file), 'r') as f:
                return f.read(), file
    return "Answer file not found.", None

def find_matches(user_input, theories, texts):
    vectorizer = TfidfVectorizer().fit(texts + [user_input])
    vectors = vectorizer.transform(texts + [user_input])
    similarity = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    matches = []
    for idx, score in enumerate(similarity):
        if score >= 0.1:
            matches.append((texts[idx], theories[idx], score))
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches

# Load data
theories = load_theories('theory.txt')
titles = [extract_question_title(theory) or "" for theory in theories]

# Streamlit UI
st.set_page_config(page_title="🧑‍💻 AI LeetCode Assistant", layout="wide")
st.title("🧑‍💻 AI LeetCode Theory & Code Assistant")

search_mode = st.sidebar.selectbox("Search Mode", ['Title-based Search', 'Theory-based Search'])

# Session state init
if 'matches' not in st.session_state:
    st.session_state.matches = []
    st.session_state.match_index = 0

def perform_search():
    query_input = st.session_state.query_input
    if not query_input:
        st.warning("Please enter a query to search.")
        return

    if search_mode == 'Title-based Search':
        matches = find_matches(query_input, theories, titles)
    else:
        matches = find_matches(query_input, theories, theories)

    if not matches:
        st.error("❌ No match found. Try a different or clearer query.")
    else:
        st.session_state.matches = matches
        st.session_state.match_index = 0

# Single input box, triggers search on Enter
st.text_input("🔍 Enter your query text:", key="query_input", on_change=perform_search)

if st.button("Search"):
    perform_search()

if st.session_state.matches:
    match_count = len(st.session_state.matches)
    idx = st.session_state.match_index
    title, theory, score = st.session_state.matches[idx]
    display_title = extract_question_title(theory) or "Untitled"

    st.subheader(f"📖 Match {idx + 1} of {match_count}")
    st.markdown(f"**Matched Title:** `{display_title}`")
    st.markdown(f"**Similarity Score:** `{score:.3f}`")

    with st.expander("📖 View Full Theory"):
        st.code(theory, language="markdown")

    slug = slugify(display_title)
    answer_code, filename = get_answer_file(slug, 'answers')

    st.markdown("### 💻 Answer Code:")
    st.code(answer_code, language="cpp")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button("⬇️ Download Code", answer_code, file_name=filename or f"{slug}.txt")
    with col2:
        st.button("📋 Copy Code", on_click=st.toast, args=("Code copied!",))
    with col3:
        if idx < match_count - 1:
            if st.button("➡️ Next Match"):
                st.session_state.match_index += 1
                st.rerun()
        else:
            st.info("✅ No more matches available.")

    with col4:
        if idx > 0:
            if st.button("⬅️ Previous Match"):
                st.session_state.match_index -= 1
                st.rerun()

    if st.button("🔙 Back to Main Menu"):
        st.session_state.clear()
        st.rerun()
