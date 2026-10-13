"""Local Streamlit UI. Session history is never shared through a global cache."""
from pathlib import Path
import hashlib
import json
import pymupdf
import streamlit as st
from ocs_qa.config import Settings, APP_ROOT
from ocs_qa.store import Store
from ocs_qa.api import ModelClient, APIError
from ocs_qa.pipeline import Pipeline

st.set_page_config(page_title="接触网规范问答",page_icon="📖",layout="wide")
st.title("接触网规范问答")
st.caption("查阅规范原文 · 区分标准版本 · 追溯回答依据")
try:
    settings=Settings.load(); store=Store(settings)
except (ValueError,OSError) as exc:
    st.error(f"配置或存储初始化失败：{exc}"); st.stop()
if "history" not in st.session_state: st.session_state.history=[]

with st.sidebar:
    st.subheader("问答设置")
    mode_label=st.selectbox("检索方式",["关键词 BM25","向量检索","混合检索"])
    mode={"关键词 BM25":"bm25","向量检索":"dense","混合检索":"hybrid"}[mode_label]
    generate=st.toggle("使用 DeepSeek 生成答案",value=False)
    st.caption("仅检索不调用问答模型；向量检索仍会调用 Embedding 接口。")
    if generate and not settings.chat_key: st.warning("尚未填写 DEEPSEEK_API_KEY。")
    if mode!="bm25" and not settings.embedding_model: st.warning("请先配置独立 Embedding 服务并构建向量。")
    if st.button("清空本次对话"):
        st.session_state.history=[]; st.rerun()
    st.divider()
    st.caption(f"问答模型：{settings.chat_model}")
    st.caption("仅查询已导入资料。文件名、年份不代表现行有效性。")

qa, kb, experiments=st.tabs(["规范问答","知识库","实验与导出"])


def show_result(result, turn):
    st.markdown(result["answer"])
    st.caption(f"状态：{result['status']} · 总耗时 {result['timings']['total_ms']:.0f} ms")
    for source in result.get("sources",[]):
        doc=source["document"]
        title=f"[来源{source['source']}] {doc['name']} · {source['location']}"
        with st.expander(title):
            st.text(source["text"])
            st.caption(f"标准：{doc['standard'] or '未识别'} · 年份：{doc['year'] or '未识别'} · 词面覆盖：{source['lexical_coverage']:.0%}")
            for claim in result.get("claims",[]):
                for cite in claim["citations"]:
                    if cite["source"]==source["source"]: st.info("引用原文："+cite["quote"])
            if source["page"] and st.button("查看 PDF 原文页",key=f"page_{turn}_{source['id']}"):
                path=Path(doc["path"])
                if not path.is_file(): st.warning("原始文件已移动；以上仍为入库时的文本。")
                elif hashlib.sha256(path.read_bytes()).hexdigest()!=doc["id"]: st.warning("原始文件已改变，请重新入库后查看。")
                else:
                    try:
                        with pymupdf.open(path) as pdf:
                            page=pdf[source["page"]-1]
                            pix=page.get_pixmap(matrix=pymupdf.Matrix(1000/page.rect.width,1000/page.rect.width))
                            st.image(pix.tobytes("png"),caption=source["location"])
                    except Exception: st.error("该页面无法预览。")


with qa:
    st.subheader("向已收录的规范提问")
    if not store.documents(): st.info("先在“知识库”导入 PDF 或 DOCX。可以不配置 API，先查看关键词检索结果。")
    st.caption("例如：TB/T 2073-2020 对零部件表面质量有什么要求？")
    for i,turn in enumerate(st.session_state.history):
        with st.chat_message("user"): st.write(turn["question"])
        with st.chat_message("assistant"): show_result(turn,i)
    question=st.chat_input("输入标准号、年份或具体问题")
    if question:
        with st.spinner("正在查找依据…"):
            result=Pipeline(store).answer(question,history=st.session_state.history,mode=mode,generate=generate)
        st.session_state.history.append(result)
        st.rerun()

with kb:
    docs=store.documents(); records=store.records()
    c1,c2,c3=st.columns(3)
    c1.metric("文档",len(docs)); c2.metric("文本片段",len(records))
    c3.metric("当前模型向量",sum(r["vector_identity"]==settings.embedding_identity for r in records))
    st.subheader("导入资料")
    uploaded=st.file_uploader("PDF / DOCX，单文件最大 100 MB",type=["pdf","docx"],accept_multiple_files=True)
    override=st.text_input("手工标准号（可选，仅对单文件导入生效）",placeholder="TB/T 2073-2020")
    allow=st.checkbox("所选资料允许向配置的模型服务发送文本",value=False)
    if st.button("解析并导入",disabled=not uploaded):
        if override and len(uploaded)!=1: st.error("手工标准号只支持一次导入一个文件。")
        else:
            reports=[]
            with st.spinner("本地解析中…"):
                for upload in uploaded:
                    raw=upload.getvalue()
                    if len(raw)>100*1024*1024:
                        reports.append({"name":upload.name,"status":"error","message":"文件超过 100 MB"}); continue
                    path=APP_ROOT/"runtime/uploads"/hashlib.sha256(raw).hexdigest()/Path(upload.name).name
                    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
                    reports.append(store.ingest(path,display_name=upload.name,allow_cloud=allow,standard_override=override or None))
            st.session_state.last_import=reports
            st.rerun()
    if "last_import" in st.session_state: st.json(st.session_state.last_import,expanded=False)
    if docs:
        st.dataframe([{"文件":d["name"],"标准":d["standard"],"年份":d["year"],"允许在线处理":d["allow_cloud"],"稿本标记":d["publication_status"],"解析提示":len(d["warnings"])} for d in docs],hide_index=True)
        byid={d["id"]:d for d in docs}
        chosen=st.multiselect("选择需要管理的文档",list(byid),format_func=lambda key:byid[key]["name"])
        a,b=st.columns(2)
        if a.button("允许所选文档在线处理",disabled=not chosen):
            store.set_cloud_permission(chosen,True); st.rerun()
        if b.button("撤销所选文档在线处理",disabled=not chosen):
            store.set_cloud_permission(chosen,False); st.rerun()
        st.caption("只在你有权向模型服务发送这些资料时开启。单纯本地检索不需要开启。")
        if st.button("补建允许在线处理文档的向量"):
            try:
                with st.spinner("调用 Embedding 服务，完成的批次会保存…"):
                    result=store.embed_pending(ModelClient(settings))
                st.success(f"新增 {result['embedded']} 个向量；{result['blocked_chunks']} 个片段未获准在线处理。")
            except APIError as exc: st.error(str(exc))
        with st.expander("移除知识库文档"):
            confirm=st.checkbox("确认仅从知识库移除所选文档，原始文件保留")
            if st.button("移除所选文档",disabled=not chosen or not confirm):
                for key in chosen: store.remove(key)
                st.rerun()
    with st.expander("最近导入记录（含跳过和失败）"): st.json(store.import_reports(),expanded=False)

with experiments:
    st.subheader("保存问答和检索记录")
    st.write("批量对比、消融和 gold 证据评测使用命令行 evaluate；运行方式见项目 README。答案正确性及引用语义支撑需人工判分。")
    data="\n".join(json.dumps(turn,ensure_ascii=False) for turn in st.session_state.history)
    st.download_button("导出本次会话 JSONL",data,file_name="ocs_session.jsonl",mime="application/jsonl",disabled=not data)
    if st.session_state.history:
        st.dataframe([{"问题":t["question"],"状态":t["status"],"检索":t["mode"],**t["timings"]} for t in st.session_state.history],hide_index=True)
