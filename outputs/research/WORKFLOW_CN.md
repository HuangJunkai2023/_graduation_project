# 开题计划执行入口

以下命令均在 `D:\_graduation_project` 运行，使用已安装的 Windows 环境。正式标准全文、参考答案、人工记录及API用量保存在被Git忽略的 `project/qa_system/runtime/research/`，仓库只保存代码、方法和不含全文的目录。

## 1. 核查题目

双击 `project/qa_system/start_review.cmd`，打开 <http://127.0.0.1:8502>。先核查 `dev-001` 到 `dev-010`，再完成剩余10道开发题及80道测试题。填写本人姓名，实际对照原始PDF/DOCX，选择通过或需要修订。操作说明见 [REVIEW_GUIDE_CN.md](REVIEW_GUIDE_CN.md)。

查看真实就绪状态，不调用模型：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research status
```

机器验证能确认配额、来源位置和摘录匹配，不能代替数值、单位、条件及语义支持的人工判断。未审核候选不算正式基准。

## 2. 开发集校准

研究库需要完整向量，补建过程可断点续做。此命令会向当前配置的硅基流动Embedding服务发送获准处理的文本：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research embed
```

20道开发题通过后执行：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research prepare --output project/qa_system/runtime/research/calibration/v1
```

仅用16道可答开发题选择 `w∈{0.25,0.50,0.75}`，按Recall@5、MRR@5及预定顺序处理并列；生成三种检索的Top-5候选段落。然后在审核页面切换“开发候选证据”，核查每个候选是否支持所问事实。

候选段落全部人工判断后：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research select --prepared project/qa_system/runtime/research/calibration/v1/selection_prepared.json --output project/qa_system/runtime/research/calibration/v1/selected.json
```

Gate候选覆盖率为0.05/0.10/0.20，余弦为0.20/0.30/0.40/0.50。先最大化三种检索的平均候选段落F1，再按问题级误拒答、精确率和固定网格顺序处理并列。阈值不是正确性概率，不证明语义充分支持。开发题、语料或候选集合变化后，旧校准作废；不要用测试输出挑参数。

## 3. 冻结与预算核对

100题全部通过、校准及向量齐全后，新建冻结版本：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research freeze --calibration project/qa_system/runtime/research/calibration/v1/selected.json --output project/qa_system/runtime/research/freezes/v1
```

冻结保存题集、语料、提示词、代码、词典及模型设置指纹，不能覆盖。之后如需更改应新建研究版本。冻结快照中的题目作为正式运行及盲评的唯一参考。

将 [budget_review.template.json](budget_review.template.json) 复制到 `runtime/research/budget_review.json`，核对两家服务的历史项目账单、当前价格和保守剩余费用，记录换算依据及真实核对人、时间。当前余额不等于历史支出；未知费用不能记为零。总预算£50，预计达到£40时按Proposal复核。不需要在文件中填写密钥。

## 4. 正式五组实验

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research run --freeze project/qa_system/runtime/research/freezes/v1 --budget project/qa_system/runtime/research/budget_review.json
```

固定80道测试题，B1 BM25、B2 Dense、B3 Hybrid、A1关闭版本检查、A2关闭Evidence Gate，共400个主要首次槽位。A1仍保留标准系列过滤；A2仍保留提示词、引用校验、模型拒答与错误处理。早期拒答也占一个测试槽位，因此400槽位不等于400次生成API请求。

运行中断可用同一命令续做，已落盘的首次结果不会被替换为较好重试。API错误和结构错误单独报告。改变冻结身份时必须使用新目录。

## 5. 人工盲评与汇总

在审核页面选择“正式结果盲评”。界面隐藏配置标签；同题答案、claims和引用证据完全相同的输出可合并核查，但保留每个原始运行槽位。逐项判断正确性、引用支持、错误版本、合理拒答与误拒答，填写依据。

全部槽位有人工评分后执行：

```powershell
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research summarize --output project/qa_system/runtime/research/measured_results.json
& ./project/qa_system/.venv-win/Scripts/python.exe -X utf8 -m ocs_qa.research report --results project/qa_system/runtime/research/measured_results.json --output project/qa_system/runtime/research/Experiment_Report_EN.md
```

主要分母：可回答64题；不可回答16题；Citation Support按已展示事实断言；Wrong-edition Rate按明确指定版本题，并区分可用与缺失版本。分母为零保持null。Recall/Correctness 0.80、Citation Support 0.90、False Refusal 0.10等均为计划目标，未达到也如实报告。

汇总同时给出分类样本数与差值，以及按group_id的成对bootstrap（seed=3801、2000次）95%区间。补充英文实验报告仅从完整人工评分汇总生成，不将小样本差异自动称为显著提升；七页最终报告仍须结合失败案例和实际来源进行解释。

## 6. 最终交付

人工评分汇总后，才能据实完成实验结果、失败分析和RQ结论。英文最终报告遵循学校模板的7页限制及字体/页边距要求；附源码、环境依赖、研究快照清单、基准审核及实验复现说明。Portfolio中的会议/反馈记录只记录真实发生的活动。演示视频使用实际系统录屏及本人英文音频，不能把预录界面当成正式测试证据。

正式标准版本对不足时，RQ2限定为可用版本约束及缺失版本行为，不推出跨版本泛化结论。本项目用于技术文档学习与查询，不能代替铁路工程认证或实际运营决策。
