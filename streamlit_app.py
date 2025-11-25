# streamlit_app.py

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from groq import Groq
import pdfplumber
import logging

# Setup
logging.basicConfig(level=logging.INFO)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Helpers

def call_llm(prompt: str, model: str = "mixtral-8x7b-32768") -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an executive strategy assistant for a CEO."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def extract_pdf_text(file) -> str:
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_csv_text(file) -> str:
    try:
        df = pd.read_csv(file)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error reading CSV: {e}"

# Modules

def generate_exec_brief(data_text: str) -> str:
    prompt = (
        "You're a Chief of Staff. Based on this data, generate an executive summary brief.\n"
        f"Data: {data_text[:6000]}"
    )
    return call_llm(prompt)

def ask_exec_question(question: str, data_text: str) -> str:
    prompt = (
        f"You are a trusted executive advisor. Given this data, answer the following question concisely:\n"
        f"Question: {question}\nData: {data_text[:6000]}"
    )
    return call_llm(prompt)

def generate_strategy_memo(data_text: str) -> str:
    prompt = (
        "You're a strategic planning assistant. Draft a company strategy memo from this input:\n"
        f"{data_text[:6000]}"
    )
    return call_llm(prompt)

# UI

def main():
    st.set_page_config("Executive Copilot AI", page_icon="🧠", layout="wide")
    st.title("🧠 Executive Copilot AI")
    st.write("Upload reports or data. Ask strategic questions. Generate board memos.")

    uploaded_files = st.file_uploader("Upload Reports (PDF or CSV)", type=["pdf", "csv"], accept_multiple_files=True)
    data_text = ""
    if uploaded_files:
        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                data_text += extract_pdf_text(file) + "\n"
            elif file.name.endswith(".csv"):
                data_text += extract_csv_text(file) + "\n"
        st.success("Files processed.")

    tab1, tab2, tab3 = st.tabs(["📋 Executive Brief", "💬 Ask a Question", "📝 Strategy Memo"])

    with tab1:
        st.subheader("📋 Generate Executive Brief")
        if st.button("Create Brief"):
            if not data_text:
                st.error("Please upload data first.")
            else:
                brief = generate_exec_brief(data_text)
                st.text_area("Executive Brief", value=brief, height=400)

    with tab2:
        st.subheader("💬 Ask a Strategic Question")
        question = st.text_input("Ask your question")
        if st.button("Answer"):
            if not question:
                st.error("Enter a question.")
            elif not data_text:
                st.error("Please upload data first.")
            else:
                answer = ask_exec_question(question, data_text)
                st.markdown(f"**AI:** {answer}")

    with tab3:
        st.subheader("📝 Generate Strategy Memo")
        if st.button("Create Memo"):
            if not data_text:
                st.error("Please upload data first.")
            else:
                memo = generate_strategy_memo(data_text)
                st.text_area("Strategy Memo", value=memo, height=400)

if __name__ == "__main__":
    main()
