"""Streamlit 网页演示（可选）。

提供"上传文档建库 + 聊天式问答 + 来源展示"的图形界面，
适合毕设答辩现场演示。启动：

    streamlit run web_app.py

注意：这只是前端展示层，底层依然通过在线 API 完成向量化和生成，
不涉及任何本地模型部署。
"""

import os
import tempfile

import streamlit as st

try:
    from .document_parser import parse_file
    from .rag_pipeline import RAGPipeline
except ImportError:
    from document_parser import parse_file
    from rag_pipeline import RAGPipeline


st.set_page_config(page_title="RAG 知识库问答演示", page_icon="📚")
st.title("📚 RAG 知识库问答演示")
st.caption("在线 API 版：文档解析 + 混合检索 + 在线大模型生成")


@st.cache_resource
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


pipeline = get_pipeline()

with st.sidebar:
    st.header("知识库")
    st.write(f"当前文本块数量：**{pipeline.vector_store.count()}**")

    uploaded = st.file_uploader("上传 PDF / DOCX", type=["pdf", "docx"])
    if uploaded and st.button("导入到知识库"):
        with st.spinner("正在解析并导入..."):
            suffix = os.path.splitext(uploaded.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.getbuffer())
                tmp_path = tmp.name
            docs = parse_file(tmp_path)
            added = pipeline.vector_store.add_documents(docs)
            st.success(f"已新增 {added} 个文本块")

    if st.button("清空知识库"):
        pipeline.vector_store.clear()
        pipeline.clear_memory()
        st.warning("知识库已清空")

    if st.button("清空对话记忆"):
        pipeline.clear_memory()
        st.info("对话记忆已清空")

# 会话级聊天记录
if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])
        for index, doc in enumerate(turn.get("sources", []), start=1):
            metadata = doc.get("metadata", {})
            with st.expander(
                f"[来源{index}] {metadata.get('file_name', 'unknown')} "
                f"第{metadata.get('page', '-')}页 融合分={doc.get('fusion_score')}"
            ):
                st.write(doc["content"])

question = st.chat_input("请输入你的问题")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("检索并生成回答..."):
            result = pipeline.answer(question)
        st.write(result["answer"])
        for index, doc in enumerate(result.get("sources", []), start=1):
            metadata = doc.get("metadata", {})
            with st.expander(
                f"[来源{index}] {metadata.get('file_name', 'unknown')} "
                f"第{metadata.get('page', '-')}页 融合分={doc.get('fusion_score')}"
            ):
                st.write(doc["content"])
    st.session_state.history.append({"question": question, **result})
