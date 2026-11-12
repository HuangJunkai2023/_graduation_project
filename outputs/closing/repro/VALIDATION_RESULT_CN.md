# 工程与研究快照交付验证

验证于2026年11月12日完成。最终公开包记录构建时Git提交`a52e9bfe73330786d73bfca0049fa91437318c06`，同时通过`PUBLIC_MANIFEST.json`的`snapshot_current_docs`保存根目录及工程README的当前工作区更新与各自哈希。冻结包的22个文件哈希逐项匹配。

| 文件 | 大小 | SHA-256 |
| --- | --- | --- |
| `OCS_Public_Code_closing-v1.zip` | 123,389 bytes | `c725b401b642e76e27b0c0bab7d7616f198d2af730ee7b78e09ceb32d0cde03a` |
| 本机`runtime/closing_delivery/closing-v1/OCS_Controlled_Research.zip` | 191,610,123 bytes | `bc24019885f6f60fb4967a828806e504a7199ebba7d414b8685d0f4aea1df13a` |
| 本机`runtime/closing_delivery/closing-v1/OCS_Controlled_Supplementary.zip` | 180,270 bytes | `e04fa22ce8d08ce2a4b81adaf7259c46f8cee812a4ae304780d8ee97ffb209fd` |

公开包包含49个工程、README与复现源文件，并附`PUBLIC_MANIFEST.json`。白名单、配置密钥字节扫描及ZIP CRC检查均通过，未收录其他ZIP或工具安装器。受控主包保留25份选定原文件、一致性SQLite备份、100题冻结基准、校准记录、400个主要首次结果、恢复尝试原始记录、主要评分及指标汇总。受控包仅保存在本机被忽略目录。

受控补充包保存27个后来归档的文件，包括8份匿名恢复核查、映射到9个槽位的恢复评分及原始输出、`resource_use.json`、API用量台账、账户余额及预算记录、案例依据和对应公开研究资源。补充包绑定主受控包及主要指标汇总哈希，恢复结果继续独立于主要400槽位。补充包已实际解压并逐项检查文件哈希和配置密钥，资源用量所记录的台账哈希与保存的原始台账一致。

已将两个真实ZIP解压到新目录，使用解压后的工程源码执行恢复。重定位25份来源文件后，原文哈希、题集、语料、向量、提示词、模型设置、源码和依赖身份全部通过`verify_freeze`检查。使用解压后的主要首次记录及评分重新计算总体指标、类别统计和成对bootstrap，生成的JSON与归档指标汇总完全相同。验证未发出外部模型请求。

另从最终公开包解压后的源码运行完整程序测试，109项全部通过，耗时19.30秒。无Git安装或无`.git`时通过公开清单读取来源提交的回退行为已单独验证。

验证使用本机已有Python 3.12.7及锁定依赖，覆盖新解压源码目录和新恢复数据库。独立电脑上的重新安装仍依赖该电脑的Python和包仓库环境。研究资料的许可继续按本机受控交付处理。

详细回执见`verification_receipt.json`和`public_receipt_closing-v1.json`。受控主包与补充包的回执、完整文件清单、解压目录和恢复数据库保存在`project/qa_system/runtime/closing_delivery/closing-v1/`。后续报告、演示文稿和视频由结题材料总索引另行列出。
