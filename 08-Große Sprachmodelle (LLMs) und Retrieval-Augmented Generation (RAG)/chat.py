"""Streamlit chat app for NASA mission RAG Q&A."""

from __future__ import annotations

import streamlit as st

from llm_client import LLMClient, LLMConfig
from rag_client import RAGClient, RAGConfig
from ragas_evaluator import RagasEvaluator

st.set_page_config(page_title="NASA Mission RAG", page_icon="🚀", layout="wide")
st.title("NASA Mission Intelligence Chat")
st.caption("Ask questions about Apollo 11, Apollo 13, and Challenger mission archives.")


@st.cache_resource
def get_rag_client() -> RAGClient:
    return RAGClient(RAGConfig())


@st.cache_resource
def get_llm_client(model: str) -> LLMClient:
    return LLMClient(LLMConfig(model=model))


@st.cache_resource
def get_evaluator() -> RagasEvaluator:
    return RagasEvaluator()


with st.sidebar:
    st.header("Settings")
    model = st.selectbox("LLM model", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"]) 
    mission = st.selectbox("Mission focus", ["all", "apollo11", "apollo13", "challenger"])
    top_k = st.slider("Retrieved chunks", min_value=2, max_value=8, value=4)
    run_eval = st.checkbox("Run quality evaluation", value=True)

rag_client = get_rag_client()
llm_client = get_llm_client(model)
evaluator = get_evaluator()

if "ui_messages" not in st.session_state:
    st.session_state.ui_messages = []

for msg in st.session_state.ui_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a NASA mission question in English...")

if question:
    st.session_state.ui_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    context, chunks = rag_client.retrieve_context(
        question=question,
        top_k=top_k,
        mission=mission,
    )
    answer = llm_client.answer_question(question=question, context=context)

    st.session_state.ui_messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

        with st.expander("Retrieved context"):
            st.text(context)

        if run_eval:
            scores = evaluator.evaluate_answer(
                question=question,
                answer=answer,
                contexts=[chunk.text for chunk in chunks],
            )
            st.subheader("Quality metrics")
            cols = st.columns(3)
            cols[0].metric("Answer relevancy", f"{scores.get('answer_relevancy', 0):.3f}")
            cols[1].metric("Faithfulness", f"{scores.get('faithfulness', 0):.3f}")
            cols[2].metric("Context precision", f"{scores.get('context_precision', 0):.3f}")
            st.caption(f"Evaluation mode: {scores.get('mode', 'unknown')}")
