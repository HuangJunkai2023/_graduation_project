"""Local human benchmark review and blinded grading; no model calls."""
from pathlib import Path
import hashlib
import json

import pymupdf
import streamlit as st

from ocs_qa.config import Settings, APP_ROOT
from ocs_qa.store import Store
from ocs_qa.study import (load_questions, validate_questions, save_review,
                          blind_tasks, save_grade, development_hash, save_passage_label, source_units)

ROOT = APP_ROOT / "runtime/research"
st.set_page_config(page_title="接触网研究核查台", page_icon="📋", layout="wide")
st.title("接触网研究核查台")
st.caption("题目原文核查 → 开发集校准 → 冻结 → 五组实验 → 盲评。此页面不调用模型服务。")
with st.sidebar:
    st.header("本地材料")
    dataset = Path(st.text_input("题集JSONL", str(ROOT / "benchmark/candidates.jsonl")))
    database = Path(st.text_input("研究知识库", str(ROOT / "kb.sqlite3")))
    reviewer = st.text_input("实际审核人姓名", placeholder="请由实际核查者填写")
    st.caption("保存时记录本人输入的姓名和实际时间；未审核不会自动计为通过。")

if not database.is_file():
    st.info("研究知识库尚未准备好。请先完成语料整理，或在左侧选择已有研究数据库。")
    st.stop()
try:
    store = Store(Settings.load(db_path=database))
    questions = load_questions(dataset)
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()


def source_panel(unit, key):
    """Show checked stored text and optionally render the original PDF page."""
    docs = {d["id"]: d for d in store.documents()}
    document = docs.get(unit.get("document_id"))
    if not document:
        st.error("该证据的文档不在当前研究库。")
        return
    st.markdown(f"**{document['name']} · {unit.get('location', '')}**")
    st.caption(f"标准：{document.get('standard')}；年份：{document.get('year')}；文档ID：{document['id'][:16]}…")
    st.text_area("待核查连续摘录", unit.get("quote", ""), height=130, disabled=True, key=f"quote-{key}")
    matches = source_units(store, unit.get("document_id"), unit.get("location"))
    with st.expander("查看此位置的已抽取文本（仍需对照原文）"):
        for r in matches:
            st.text(r["text"])
    path = Path(document["path"])
    if path.is_file():
        if path.suffix.lower() == ".pdf" and matches and matches[0].get("page"):
            if st.button("显示PDF原文页", key=f"pdf-{key}"):
                if hashlib.sha256(path.read_bytes()).hexdigest() != document["id"]:
                    st.error("源文件已改变，不能沿用旧文档身份核查。")
                else:
                    try:
                        with pymupdf.open(path) as pdf:
                            page = pdf[matches[0]["page"] - 1]
                            pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5))
                            st.image(pix.tobytes("png"), caption=unit.get("location"), width="stretch")
                    except Exception as exc:
                        st.error(f"原文页不能预览：{type(exc).__name__}")
        st.caption(f"本机原文件：{path}")
    else:
        st.warning("源文件路径不可用，请先恢复与哈希一致的原文件，勿仅凭抽取文本通过。")


review_tab, passages_tab, grade_tab, readiness_tab = st.tabs(["① 题目原文核查", "② 开发候选证据", "③ 正式结果盲评", "④ 冻结就绪情况"])
with review_tab:
    if not questions:
        st.info("候选题集尚未生成。题目出现后可先核查10道开发题，再分批处理其余题目。")
    else:
        counts = validate_questions(questions, store)
        a, b, c = st.columns(3)
        a.metric("候选题", len(questions))
        b.metric("人工已通过", counts["approved"])
        c.metric("待核查／修订", len(questions) - counts["approved"])
        st.info("先核对问题、原文位置、必要事实、数值／单位／条件，再明确选择通过或待修订。页面不会替代人工判断。")
        first, second = st.columns(2)
        split = first.selectbox("划分", ["dev", "test", "全部"], format_func=lambda x: {"dev": "开发集", "test": "测试集", "全部": "全部"}[x])
        state = second.selectbox("筛选审核状态", ["未通过的题目", "unreviewed", "needs_revision", "approved", "全部"])
        selected_rows = [q for q in questions if (split == "全部" or q.get("split") == split)
                         and (state == "全部" or (state == "未通过的题目" and q.get("review_status") != "approved")
                              or q.get("review_status") == state)]
        if not selected_rows:
            st.success("当前筛选下没有题目。可切换划分或状态继续核查。")
        else:
            by_id = {q["question_id"]: q for q in selected_rows}
            qid = st.selectbox("题号", list(by_id), format_func=lambda k: f"{k} · {by_id[k].get('category')} · {by_id[k].get('question', '')[:55]}")
            q = by_id[qid]
            left, right = st.columns([1, 1])
            with right:
                st.subheader("证据与原文")
                if q["answerable"]:
                    for i, unit in enumerate(q.get("evidence_units", [])):
                        source_panel(unit, f"{qid}-{i}")
                else:
                    st.write("预标为不可回答；请核对缺版／库外／无关／信息冲突的理由，不能只因检索未命中就判不可答。")
                    st.write(q.get("unanswerable_reason", ""))
                st.caption("同一事实或对话不得跨划分。需要改变题型、分组或可回答性时，先标为待修订，再调整候选集并重新验证配额。")
            with left:
                st.subheader("题目与判分依据")
                st.caption(f"group_id：{q.get('group_id')}；可回答：{q.get('answerable')}；状态：{q.get('review_status')}")
                if q.get("history"):
                    st.json(q["history"])
                with st.form(f"review-{qid}"):
                    question = st.text_area("问题", q["question"], height=95)
                    reference = st.text_area("参考答案", q.get("reference_answer", ""), height=130)
                    facts = st.text_area("必要事实（每行一项，可答题1–3项）", "\n".join(q.get("required_facts", [])), height=100)
                    evidence = st.text_area("证据JSON（只填准确连续摘录与位置）", json.dumps(q.get("evidence_units", []), ensure_ascii=False, indent=2), height=190)
                    reason = st.text_area("不可回答理由（可答题可留空）", q.get("unanswerable_reason", ""))
                    status = st.selectbox("本次决定", ["请选择", "approved", "needs_revision", "unreviewed"], format_func=lambda x: {"请选择":"请选择", "approved":"已对照原文，通过", "needs_revision":"需要修订", "unreviewed":"撤回为未审核"}[x])
                    notes = st.text_area("核查记录／待修订问题", q.get("review_notes", ""))
                    submitted = st.form_submit_button("保存本次人工决定")
                if submitted:
                    try:
                        if status == "请选择":
                            raise ValueError("请明确选择本次审核决定。")
                        save_review(dataset, qid, reviewer=reviewer, status=status, notes=notes, store=store,
                                    edits={"question": question, "reference_answer": reference,
                                           "required_facts": [v.strip() for v in facts.splitlines() if v.strip()],
                                           "evidence_units": json.loads(evidence), "unanswerable_reason": reason})
                        st.success("已记录该题审核，刷新后可继续下一题。")
                        st.rerun()
                    except (ValueError, OSError) as exc:
                        st.error(str(exc))

with passages_tab:
    labels_path = ROOT / "benchmark/passage_labels.jsonl"
    try:
        labels = load_questions(labels_path)
    except (ValueError, OSError) as exc:
        st.error(str(exc))
        labels = []
    if not labels:
        st.info("先审核开发题，再生成三种检索方式的开发候选段落。每个问题／文本块合并核查；未生成标签不会自动通过。")
    else:
        st.subheader("用于Evidence Gate阈值选择的人工段落标签")
        approved = sum(r.get("review_status") == "approved" and type(r.get("relevant")) is bool for r in labels)
        st.metric("已核查候选", f"{approved} / {len(labels)}")
        show_reviewed = st.checkbox("显示已核查候选", key="passages-reviewed")
        choices = {r["label_id"]: r for r in labels if show_reviewed or r.get("review_status") != "approved"}
        if not choices:
            st.success("所有当前开发候选均已人工核查。")
        else:
            label_id = st.selectbox("候选证据编号", list(choices))
            label = choices[label_id]
            left, right = st.columns(2)
            with left:
                st.write("**问题：**" + label.get("question", ""))
                q = next((q for q in questions if q["question_id"] == label.get("question_id")), None)
                if q:
                    st.write("**必要事实：**")
                    for fact in q.get("required_facts", []): st.write("• " + fact)
                    st.write("**参考答案：**" + q.get("reference_answer", ""))
                st.info("请根据原文判断候选是否支持问题所需事实。仅提到相同术语不代表相关；不是gold摘录也不一定是不相关。自动建议不计为人工标签。")
                with st.form(f"passage-{label_id}"):
                    verdict = st.selectbox("该候选能否支持问题所需事实？", ["请选择", "是", "否"])
                    note = st.text_area("核查说明", label.get("review_reason", ""))
                    submit_passage = st.form_submit_button("保存该候选的人工标签")
                if submit_passage:
                    try:
                        if verdict == "请选择": raise ValueError("请明确选择是或否。")
                        save_passage_label(labels_path, label_id, reviewer=reviewer,
                                           relevant=verdict == "是", notes=note)
                        st.rerun()
                    except (ValueError, OSError) as exc:
                        st.error(str(exc))
            with right:
                source = label.get("source", {})
                source_panel({"document_id": source.get("document_id"), "location": source.get("location"),
                              "quote": source.get("text", "")}, f"passage-{label_id}")

with grade_tab:
    result_dir = ROOT / "results"
    grades_path = ROOT / "scoring/grades.jsonl"
    # Only the five predeclared runs belong in blinded scoring. Private task
    # exports, event logs and resumed diagnostics are not additional runs.
    result_files = [result_dir / f"{label}.jsonl" for label in ["B1", "B2", "B3", "A1", "A2"]
                    if (result_dir / f"{label}.jsonl").is_file()]
    if not result_files:
        st.info("正式实验尚未输出结果。本页不会自行启动实验或替你评分。")
    else:
        try:
            tasks = blind_tasks(result_files)
            existing = {g["blind_id"]: g for g in load_questions(grades_path)}
            st.caption("配置标签和运行文件名不在页面展示。只有答案、claims及证据完全相同的记录才合并评分。")
            show_done = st.checkbox("也显示已评分条目")
            available = [t for t in tasks if show_done or t["blind_id"] not in existing]
            st.metric("盲评进度", f"{len(existing)} / {len(tasks)}")
            if not available:
                st.success("当前条目均已评分。")
            else:
                mapping = {t["blind_id"]: t for t in available}
                bid = st.selectbox("盲评编号", list(mapping))
                task = mapping[bid]
                # Formal grading must use the immutable question actually run,
                # never a subsequently edited candidate with the same ID.
                q = task.get("question_snapshot")
                left, right = st.columns(2)
                with left:
                    st.subheader("问题与必要事实")
                    st.write(q["question"] if q else task["question_id"])
                    if q:
                        if q.get("history"): st.json(q["history"])
                        st.write(q.get("reference_answer", ""))
                        for f in q.get("required_facts", []): st.write("• " + f)
                        st.caption(f"预标可回答性：{q.get('answerable')}；预期行为：{q.get('expected_action')}")
                        with st.expander("查看冻结gold证据与原文位置"):
                            for i, unit in enumerate(q.get("evidence_units", [])):
                                source_panel(unit, f"gold-{bid}-{i}")
                            if not q.get("evidence_units"):
                                st.write(q.get("unanswerable_reason", "无gold证据；请核对不可答理由。"))
                    else:
                        st.error("该记录缺少冻结题目快照，不能使用当前候选题替代正式判分依据。")
                    st.subheader("系统回答")
                    st.write(task["result"].get("answer", ""))
                    st.caption("返回状态：" + str(task["result"].get("status")))
                with right:
                    st.subheader("本次回答的来源")
                    for i, source in enumerate(task["result"].get("sources", [])):
                        st.markdown(f"**来源 {source.get('source', i + 1)}**")
                        source_panel({"document_id": source.get("document_id"), "location": source.get("location"), "quote": source.get("text", "")}, f"blind-{bid}-{i}")
                options = ["请选择", "是", "否", "不适用"]
                with st.form(f"grade-{bid}"):
                    correct = st.selectbox("回答是否完全正确（含版本、数值、单位及条件）", options)
                    support = []
                    for i, claim in enumerate(task["result"].get("claims", []), 1):
                        st.write(f"Claim {i}: {claim.get('text', '')}")
                        for j, citation in enumerate(claim.get("citations", []), 1):
                            st.caption(f"引文 {j} → 来源 {citation.get('source', '未提供')}")
                            st.text(citation.get("quote", ""))
                        support.append(st.selectbox(f"Claim {i}是否由整组引文共同充分支持", ["请选择", "是", "否"]))
                    wrong = st.selectbox("是否使用非请求版本作答", options)
                    justified = st.selectbox("是否属于合理拒答／必要澄清", options)
                    false = st.selectbox("是否错误拒绝或不必要澄清了可答题", options)
                    failure = st.selectbox("主要失败类型", ["none", "api_error", "retrieval_miss", "wrong_edition", "unsupported", "false_refusal", "other"])
                    why = st.text_area("判分理由与核查依据")
                    save = st.form_submit_button("保存人工评分")
                if save:
                    try:
                        if not q: raise ValueError("缺少冻结题目快照，无法保存正式评分。")
                        fields = [correct, wrong, justified, false]
                        if "请选择" in fields or "请选择" in support:
                            raise ValueError("请逐项评分；确不适用时明确选择不适用。")
                        decode = {"是": True, "否": False, "不适用": None}
                        save_grade(grades_path, task, reviewer=reviewer, correct=decode[correct],
                                   claim_support=[v == "是" for v in support], wrong_edition=decode[wrong],
                                   justified_refusal=decode[justified], false_refusal=decode[false],
                                   failure_type=failure, reason=why)
                        st.success("评分已保存。")
                        st.rerun()
                    except (ValueError, OSError) as exc:
                        st.error(str(exc))
        except (ValueError, OSError) as exc:
            st.error(str(exc))

with readiness_tab:
    full = validate_questions(questions, store, require_full=True, require_approved=True)
    st.subheader("题集就绪检查")
    st.json({k: v for k, v in full.items() if k != "errors"})
    if full["errors"]:
        st.warning("尚未满足冻结条件。")
        st.write("\n".join(full["errors"][:30]))
    else:
        st.success("题集配额、证据位置和人工通过记录齐全；仍需核对开发集校准、当前向量及配置冻结。")
    if questions:
        st.caption("开发集指纹：" + development_hash(questions))
    st.write("后续顺序：仅用已审核开发题选择权重与门槛 → 记录校准依据 → 冻结题集、语料、代码和配置 → 五组正式运行。")
    st.caption("此页面不会把默认参数、机器抽取或模型输出自动升级为人工确认或实验结论。")
