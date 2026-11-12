# 研究语料清单与核查记录

截至2026年11月12日，本机研究库为25份独立编号标准、3341个文本块。筛查1051个PDF/DOCX文件，按主题和编号初筛138个候选（含23个从合订本导出的独立标准）。全文、抽取样本与数据库只保存在被Git忽略的本机目录。

- `manifest.json`：选定来源、文件哈希、标准编号、年份、块数及权限声明。
- `candidate_inventory.json`：候选与排除理由，不含标准全文。
- `verification.json`：来源哈希、数据库成员、块数和合订本页码映射的确定性检查。
- `cover_observations.json`：封面图像或DOCX前部文字的编号、年份观察记录；不冒充学生人工复核。
- `review_summary.md`：选定来源的简表。

25份独立标准来自15个原始文件，其中11份为Q/CR 979-2023合订本内具有独立编号、封面和发布信息的分部分标准，不是把任意章节计作文档。导出PDF保留原页内容，manifest记录原合订本哈希、原文件页码区间、导出文件哈希及页码偏移。机器核查逐页比较了导出页与原页的尺寸和文字。

Q/CR 9523-2018技术部分存在“2018—xx—xx”日期占位，已保守排除。若干分部分标准同样存在未解决的发布信息占位，也未选入。当前选定语料中没有已取得的同系列双正式版本。因此RQ2只能研究“已有版本／请求版本缺失”的过滤行为；不能声称已经验证不同正式版本之间的选择能力。题目出现缺失年份时只表示请求语料未收录的年份，不证明该正式版本实际存在。

源文件字节与25份文档／3341块的manifest、数据库记录一致，11份导出标准的页码映射检查通过。封面编号／年份可观察不等于正式有效性认证；表格、数字、单位、条件和答案语义仍须人工核对。所有人工质量批准状态均保留为待复核。

可重新运行本地来源检查：

```python
from pathlib import Path
from ocs_qa.corpus import verify_manifest
from ocs_qa.config import Settings
from ocs_qa.store import Store

report = verify_manifest(
    Path('../../outputs/research/corpus/manifest.json'),
    Store(Settings.load(db_path='runtime/research/kb.sqlite3')),
)
assert report['valid'], report['errors']
```

在`project/qa_system`目录运行；该检查不调用外部API，也不会改动来源文件或将题目自动标成已审核。
