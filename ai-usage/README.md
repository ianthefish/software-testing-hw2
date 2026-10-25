# AI 使用紀錄索引

Q1、Q2、Q3、Q6、Q7 均使用本次主對話（main-session.md）。為避免重複抄寫或漏掉跨題提示，完整主對話只附一次，所有題目均引用該檔。Q2 的盲修 session 另見 Q2-new-agent.md；Q7 的只給測試 session 另見 Q7-new-agent.md。對應 JSON 保留完整逐字內容。兩個新 session 的實際委派 prompt 另存 prompts/，並已納入各 session 正文。

user-supplied-procedure.txt 是使用者主 prompt 提供的完整文字附件。它含先前準備流程，但無法由此還原產生該附件的過往 AI 對話，不宣稱那些未提供的 prompts 或回覆已取得。原始 PDF 另保存在 original/。

AI 模型與 CLI 版本取自這幾個實際 session 的本機 metadata，不猜測未提供的模型快照版。匯出使用者提示、委派 prompt 及完整可見文字回覆；不匯出內部推理、系統／開發者指令或憑證。低層工具參數部分以受保護格式存於 session，不將不可讀內容誤列為 prompt。測試及 CI 原始工具輸出已另存 evidence/，程式、測試列印本與完整 Git 歷史保留實際編輯結果。

這是截至 manifest 中時間的完整工作對話快照；打包後的交付連結訊息不參與程式生成。所有本次使用的 prompt 及使用者審查回覆均在快照中。
