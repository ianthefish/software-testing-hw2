# Calc TDD 作業

包含 Q1、Q2、Q3、Q6、Q7；依要求略過 Q4、Q5。

## 執行

使用 Python 3.12。建立虛擬環境後安裝 requirements-dev.txt：

這台電腦的 `python` / `py` 尚未能直接使用；已驗證的基礎 Python 是 `C:\Users\ianyu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。第一次建立環境可執行 `& 'C:\Users\ianyu\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv`，之後使用下列 `.venv` 指令。其他電腦可使用已安裝的 Python 3.12。

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe -m coverage run -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe -m coverage report
```

Q7 必須在它自己的工作目錄執行，才會測到保留的首次 agent 實作：

```powershell
Push-Location experiments/q7
& ..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
Pop-Location
```

## 檔案索引

- calculator.py：最終 Calc。
- tests/：Q1 與經使用者審查的 Q6 測試。
- original/：原始附件。
- reports/：逐題敘事、規格及限制。
- evidence/：實際 Red/Green 輸出、SHA-256、CI run metadata 與截圖。
- experiments/q2/：新 session 的盲修復結果與證據。
- experiments/q7/：只依 Q1 測試產生的首次 Calc 與後加的變形測試。
- ai-usage/：逐字 prompts、完整可見回覆、委派 prompt 及來源資訊。
- output/pdf/：正式報告、程式與測試列印本、AI 使用紀錄附錄。

Q1 完成點固定在 q1-complete；Q6 的測試提交 563359b 在實作提交 b1b377f 之前。Q2 的五次 CI 結果與連結列於 reports/Q2.md。完整提交歷史另以 Git log 與 bundle 隨繳交壓縮檔附上。

## 運算契約

輸入以整數為本作業驗證範圍。加減乘為整數運算；divide 回 float，除零拋 ValueError。modulo 採 Python 餘數規則，除零拋 ZeroDivisionError。power 採 Python 規則，0^0=1，負指數回 float，0 的負次方拋 ZeroDivisionError。

## 流程揭露

使用者表示先前已自行做過 Q1，要求本次由 agent 重做。這次保留的 Q1 歷史與 Q2 第一次參照修復由 agent 實際執行，不能充作無 AI 的本人操作證據。Q6 有本次實際人工審查與授權代為提交的紀錄。詳細限制已在各題報告說明。

截圖為瀏覽器擷取的真實執行紀錄展示頁，原始指令輸出和來源雜湊均附上；不將展示頁冒稱為終端機介面。
