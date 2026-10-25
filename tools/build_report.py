"""Build the report and verbatim AI appendix from saved project evidence."""

from datetime import datetime, timezone, timedelta
import html
import json
from pathlib import Path
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                               Table, TableStyle, Image, Preformatted, KeepTogether)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("JhengHei", "C:/Windows/Fonts/msjh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("JhengHeiBold", "C:/Windows/Fonts/msjhbd.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("Code", "C:/Windows/Fonts/consola.ttf"))
pdfmetrics.registerFontFamily("JhengHei", normal="JhengHei", bold="JhengHeiBold")
NAVY = colors.HexColor("#132B49")
TEAL = colors.HexColor("#176B6B")
PALE = colors.HexColor("#EEF3F7")
GRAY = colors.HexColor("#52637A")
WIDTH = A4[0] - 88

STYLES = {
    "body": ParagraphStyle("body", fontName="JhengHei", fontSize=9.5, leading=14,
                           spaceAfter=6, textColor=NAVY, wordWrap="CJK"),
    "h1": ParagraphStyle("h1", fontName="JhengHeiBold", fontSize=21, leading=29,
                         spaceBefore=6, spaceAfter=17, textColor=NAVY, keepWithNext=True),
    "h2": ParagraphStyle("h2", fontName="JhengHeiBold", fontSize=12, leading=17,
                         spaceBefore=10, spaceAfter=6, textColor=TEAL, keepWithNext=True),
    "small": ParagraphStyle("small", fontName="JhengHei", fontSize=8, leading=12,
                            spaceAfter=6, textColor=GRAY, wordWrap="CJK"),
    "cell": ParagraphStyle("cell", fontName="JhengHei", fontSize=8.5, leading=13,
                           textColor=NAVY, wordWrap="CJK"),
    "code": ParagraphStyle("code", fontName="Code", fontSize=8.2, leading=11,
                           textColor=NAVY, backColor=PALE, borderPadding=8, spaceAfter=8),
    "verbatim": ParagraphStyle("verbatim", fontName="JhengHei", fontSize=9, leading=13.5,
                               spaceAfter=4, textColor=NAVY, wordWrap="CJK"),
}


def p(text, style="body"):
    return Paragraph(html.escape(text).replace("\n", "<br/>"), STYLES[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DFE9"))
    canvas.line(44, 44, A4[0] - 44, 44)
    canvas.setFont("JhengHei", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(44, 30, "CALC TDD  |  software-testing-hw2  |  2026-10-25")
    canvas.drawRightString(A4[0] - 44, 30, str(doc.page))
    canvas.restoreState()


def document(path, story, title):
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=44, leftMargin=44,
                            topMargin=45, bottomMargin=60,
                            title=title, author="Calc TDD project", pageCompression=1)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def md_blocks(text):
    lines, result, index = text.splitlines(), [], 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [s.strip() for s in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+", cell) for cell in cells):
                    rendered = []
                    for cell in cells:
                        if cell.startswith("https://github.com/ianthefish/software-testing-hw2/actions/runs/"):
                            rendered.append(Paragraph(f'<link href="{cell}" color="#176B6B">Run {cell.rsplit("/",1)[-1]}</link>', STYLES["cell"]))
                        else:
                            rendered.append(p(cell, "cell"))
                    rows.append(rendered)
                index += 1
            columns = len(rows[0])
            # URLs in Q2 need a wider final column.
            widths = [75, 65, 60, WIDTH - 200] if columns == 4 else [WIDTH / columns] * columns
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PALE),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, TEAL),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#D5DFE9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            result.extend([table, Spacer(1, 10)])
            continue
        if line.startswith("# "):
            result.append(p(line[2:], "h1"))
        elif line.startswith("## "):
            result.append(p(line[3:], "h2"))
        else:
            paragraph = [line]
            while index + 1 < len(lines) and lines[index + 1].strip() and not lines[index + 1].lstrip().startswith(("#", "|", "- ", ">")):
                index += 1
                paragraph.append(lines[index].strip())
            result.append(p("\n".join(paragraph)))
        index += 1
    return result


def code_block(path):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    display = []
    for number, line in enumerate(lines, 1):
        segments = textwrap.wrap(line, width=94, expand_tabs=False, replace_whitespace=False,
                                 drop_whitespace=False, break_long_words=True, break_on_hyphens=False) or [""]
        display.append(f"{number:3}  {segments[0]}")
        display.extend("     " + part for part in segments[1:])
    return Preformatted("\n".join(display), STYLES["code"])


def screenshot(path, caption):
    from PIL import Image as PILImage
    with PILImage.open(path) as src:
        width, height = src.size
    target_width = WIDTH * 0.93
    return [p(caption, "h2"), Image(str(path), width=target_width, height=target_width * height / width), Spacer(1, 6)]


def build_main():
    story = [Spacer(1, 45), p("SOFTWARE TESTING / HOMEWORK 2", "small"),
             p("Calc：測試驅動開發<br/>與 AI Agent 實驗".replace("<br/>", "\n"), "h1"),
             p("Q1、Q2、Q3、Q6、Q7 完整實作與證據報告", "h2"),
             p("提交帳號：ianthefish\n日期：2026 年 10 月 25 日\n語言：Python 3.12\n測試：unittest；驗證工具：coverage.py 7.17.0"),
             Spacer(1, 18)]
    summary = [[p("驗證項目", "cell"), p("實際結果", "cell")],
               [p("最終 Calc", "cell"), p("6 個測試方法全部通過", "cell")],
               [p("Q7 保存的首次實作", "cell"), p("10 個測試方法全部通過；未觀察到固定輸入特判", "cell")],
               [p("產品覆蓋率", "cell"), p("15 / 15 語句；2 / 2 分支；100%", "cell")],
               [p("Q2 雲端故障實驗", "cell"), p("success → failure → success → failure → success", "cell")],
               [p("Q6 審查順序", "cell"), p("實際 Red → 人工審查 → 測試 commit → 實作 commit → Green", "cell")]]
    t = Table(summary, colWidths=[145, WIDTH-145])
    t.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),PALE), ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#D5DFE9")),
                           ("VALIGN",(0,0),(-1,-1),"TOP"), ("TOPPADDING",(0,0),(-1,-1),10), ("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story += [t, Spacer(1, 20), p("流程限制", "h2"),
              p("本次 Q1 重做及 Q2 第一次參照修復由 agent 執行，不能證明無 AI 的人工獨立完成。Q6 有實際人工審查；以一個 test method 的 17 組 subTest 合併為一輪。各題如實記錄，並附逐字 AI 使用紀錄。"),
              p("GitHub：https://github.com/ianthefish/software-testing-hw2", "small"), PageBreak()]
    story += [p("閱讀與繳交索引", "h1"),
              p("本報告依序包含：Q1 四輪 Red/Green 敘事、Q2 五階段 CI 與盲修比較、Q3 覆蓋率驗證、Q6 人工審查及規則紀錄、Q7 變形測試、實際截圖、程式與測試列印本、Git 提交圖。"),
              p("AI-usage-log.pdf 是逐字提示與完整可見回覆附錄；ai-usage/ 另有可機讀 JSON 與新 session 的委派 prompt。evidence/ 保存每次執行輸出、exit code、來源雜湊、雲端 metadata 及原始 CI log ZIP。"),
              p("壓縮檔另附完整 Git log 與可重建歷史的 Git bundles。Q1 起點與完成點、Q6 測試及實作先後、Q2 故障狀態均可由歷史檢查。Q4 與 Q5 依使用者指定略過。"),
              p("原始資料", "h2"),
              p("原始 PDF 與 Calc.py、CalcTest.py 保存在 original/。附件已含減乘除，且測試匯入名稱與檔名不同，因此保留附件並另建 add-only baseline；沒有覆寫原始檔案。"),
              p("版本與證據時間", "h2"),
              p("功能與 coverage 雲端驗證固定在 b890fd7f3939e9d78a26d27ec856474e30cdd9f3。後續提交整理文件及證據；打包後的 manifest 記錄實際 repository HEAD 與最後 CI run，避免把較早綠燈當成最後提交的驗證。"), PageBreak()]
    for q in ["Q1", "Q2", "Q3", "Q6", "Q7"]:
        story += md_blocks((ROOT / "reports" / f"{q}.md").read_text(encoding="utf-8"))
        story.append(PageBreak())
    shots = ROOT / "evidence/screenshots"
    story += [p("測試與 CI 截圖", "h1"), p("以下本機截圖為瀏覽器擷取的實際輸出展示頁，文字來源、指令、測試數及退出碼均保留。原始 txt/json 與展示頁另附，可核對來源雜湊。GitHub 圖片則直接截取真實 Actions 頁面。", "small")]
    for i, (file, caption) in enumerate([
        ("q1-tests-pass.jpg", "Q1：5 個測試全部通過"),
        ("q6-tests-pass.jpg", "Q6：經審查的契約與既有測試全部通過"),
        ("q3-coverage.jpg", "Q3：15 個語句與 2 個分支全部覆蓋"),
        ("github-q3-success.jpg", "GitHub Actions：整合驗證成功"),
        ("q7-metamorphic-pass.jpg", "Q7：原測試與後加變形測試全部通過"),
        ("final-tests-pass.jpg", "最終 Calc：全部測試通過"),
    ]):
        if i and i % 2 == 0:
            story.append(PageBreak())
        story += screenshot(shots / file, caption)
    source_groups = [["calculator.py", ".coveragerc", "requirements-dev.txt"],
                     ["tests/test_calculator.py"], ["tests/test_q6.py"],
                     ["experiments/q7/calculator.py", ".github/workflows/ci.yml"],
                     ["experiments/q7/tests/test_metamorphic.py"]]
    for group in source_groups:
        story += [PageBreak(), p("程式與測試列印本", "h1")]
        for filename in group:
            story += [p(filename, "h2"), code_block(ROOT / filename)]
    story += [PageBreak(), p("Git 提交圖", "h1"), p("完整作者、時間、差異統計見隨附 git-log-full.txt。Q2 與 Q7 的獨立 agent 專案另有專屬 Git log 及 bundle。", "small"),
              code_block(ROOT / "evidence/git-log-graph.txt")]
    document(OUT / "CalcTDD-report.pdf", story, "Calc TDD 作業報告")


def build_ai():
    story = [p("AI 使用紀錄：逐字附錄", "h1"),
             p("適用題目：Q1、Q2、Q3、Q6、Q7。主對話全文只附一次；另附 Q2 盲修及 Q7 tests-only 新 session。"),
             p("工具與模型版本由實際 session metadata 取得。下列內容保留 prompts、完整可見文字回覆與人工審查原文。原始 JSON 可核對逐字內容；新 agent 的委派 prompt 另有文字檔，程式及測試亦有列印本與 Git 歷史。內部推理、系統／開發者指令及憑證不屬於此公開附錄。"),
             p("這是工作對話截至下列 cutoff 的快照。打包完成後的交付連結訊息不參與程式生成。", "small")]
    for label in ["main-session", "Q2-new-agent", "Q7-new-agent"]:
        data = json.loads((ROOT / "ai-usage" / f"{label}.json").read_text(encoding="utf-8"))
        story += [PageBreak(), p(label, "h1"),
                  p(f"工具：{data['tool']}\n模型：{', '.join(data['models'])}\nCLI 版本：{data['cli_version']}\n模型快照版本：未提供\n紀錄截止（UTC）：{data['cutoff_utc']}", "small")]
        for index, message in enumerate(data["messages"], 1):
            story += [p(f"{index}. {message['role']} / {message['timestamp']}", "h2")]
            for block in message["text"].split("\n\n"):
                if block:
                    story.append(p(block, "verbatim"))
                else:
                    story.append(Spacer(1, 4))
    story += [PageBreak(), p("使用者提供的文字附件全文", "h1"),
              p("這是本次 prompt 附帶的步驟原文。內容中的先前對話與範例 prompt 不表示本次實際執行過，也不據此補造未提供的舊對話。", "small")]
    attachment = (ROOT / "ai-usage/user-supplied-procedure.txt").read_text(encoding="utf-8")
    for block in attachment.split("\n\n"):
        if block:
            story.append(p(block, "verbatim"))
    document(OUT / "AI-usage-log.pdf", story, "Calc TDD AI 使用逐字附錄")


if __name__ == "__main__":
    build_main()
    build_ai()
    print("Created:")
    for path in OUT.glob("*.pdf"):
        print(path.name, path.stat().st_size)
