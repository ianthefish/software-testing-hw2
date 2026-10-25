"""Export user prompts, visible assistant replies, and review questions.

Internal instructions, reasoning, credentials, and raw session metadata are not
published. Actual test/CI tool outputs are preserved separately in evidence/.
"""

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import shutil


def export_session(path, label, destination, initial_prompt=None):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    metadata = next(row["payload"] for row in rows if row["type"] == "session_meta")
    models = list(dict.fromkeys(row["payload"].get("model") for row in rows
                              if row["type"] == "turn_context" and row["payload"].get("model")))
    messages, calls = [], []
    if initial_prompt:
        messages.append({"timestamp": initial_prompt["timestamp"], "role": "task-prompt-from-parent",
                         "text": initial_prompt["text"]})
    for row in rows:
        if row["type"] != "response_item":
            continue
        item = row["payload"]
        kind = item.get("type")
        if kind == "message" and item.get("role") in {"user", "assistant"}:
            if item.get("channel") == "analysis":
                continue
            text = "\n".join(part.get("text", "") for part in item.get("content", [])
                             if part.get("type") in {"input_text", "output_text", "text"})
            if not text.strip() or text.startswith("<environment_context>") or text.startswith("<external_codex_apps_open_page>"):
                continue
            messages.append({"timestamp": row["timestamp"], "role": item["role"],
                             "phase": item.get("phase"), "text": text})
        elif kind in {"function_call", "custom_tool_call"}:
            call = {"timestamp": row["timestamp"], "type": kind,
                    "namespace": item.get("namespace"), "name": item.get("name"),
                    "arguments": item.get("arguments"), "input": item.get("input")}
            calls.append(call)
            if item.get("name") == "request_user_input_async":
                messages.append({"timestamp": row["timestamp"], "role": "assistant-question",
                                 "text": item.get("arguments", "")})

    record = {"label": label, "session_id": metadata.get("id"), "tool": "Codex Desktop",
              "models": models, "cli_version": metadata.get("cli_version"),
              "model_snapshot_version": "Not provided", "cutoff_utc": rows[-1]["timestamp"],
              "messages": messages}
    (destination / f"{label}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [f"# {label} - AI 使用逐字紀錄", "", "工具：Codex Desktop",
             f"模型：{', '.join(models) or '未提供'}", f"可取得的 CLI 版本：{metadata.get('cli_version', '未提供')}",
             "模型快照版本：未提供；CLI 版本不等於模型版本。",
             f"本檔收錄至（UTC）：{record['cutoff_utc']}",
             "下列使用者 prompts、agent 可見文字回覆及審查問題皆保留原文，不以摘要代替。",
             "實際測試與 CI 原始輸出見 evidence/；完整程式與編輯順序見列印本及 Git 歷史。", ""]
    for i, message in enumerate(messages, 1):
        lines.extend([f"## {i}. {message['role']} | {message['timestamp']}", "", message["text"], ""])
    (destination / f"{label}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {k: v for k, v in record.items() if k != "messages"} | {"message_count": len(messages), "tool_call_count": len(calls)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session", type=Path)
    parser.add_argument("--output", type=Path, default=Path("ai-usage"))
    parser.add_argument("--attachment", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parent = json.loads(args.session.open(encoding="utf-8").readline())["payload"]["id"]
    sessions = [(args.session, "main-session", None)]
    task_prompts = {}
    for line in args.session.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        item = row.get("payload", {})
        if row["type"] == "response_item" and item.get("name") == "spawn_agent":
            arguments = json.loads(item["arguments"])
            task_prompts[arguments["task_name"]] = {"timestamp": row["timestamp"], "text": arguments["message"]}
    for path in args.session.parent.glob("*.jsonl"):
        meta = json.loads(path.open(encoding="utf-8").readline()).get("payload", {})
        source = meta.get("source")
        spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
        if spawn.get("parent_thread_id") == parent:
            label = {"/root/q2_blind_repair": "Q2-new-agent", "/root/q7_tests_only": "Q7-new-agent"}.get(spawn.get("agent_path"))
            if label:
                prompt = task_prompts.get(spawn["agent_path"].split("/")[-1])
                # The session store may protect tool-argument text. Use the exact
                # prompt saved from the actual issued collaboration call.
                if prompt and prompt["text"].startswith("gAAAA"):
                    prompt["text"] = (args.output / "prompts" / f"{label}.txt").read_text(encoding="utf-8").rstrip("\n")
                sessions.append((path, label, prompt))
    manifest = [export_session(path, label, args.output, prompt) for path, label, prompt in sessions]
    if args.attachment:
        shutil.copyfile(args.attachment, args.output / "user-supplied-procedure.txt")
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output / "README.md").write_text("""# AI 使用紀錄索引

Q1、Q2、Q3、Q6、Q7 均使用本次主對話（main-session.md）。為避免重複抄寫或漏掉跨題提示，完整主對話只附一次，所有題目均引用該檔。Q2 的盲修 session 另見 Q2-new-agent.md；Q7 的只給測試 session 另見 Q7-new-agent.md。對應 JSON 保留完整逐字內容。兩個新 session 的實際委派 prompt 另存 prompts/，並已納入各 session 正文。

user-supplied-procedure.txt 是使用者主 prompt 提供的完整文字附件。它含先前準備流程，但無法由此還原產生該附件的過往 AI 對話，不宣稱那些未提供的 prompts 或回覆已取得。原始 PDF 另保存在 original/。

AI 模型與 CLI 版本取自這幾個實際 session 的本機 metadata，不猜測未提供的模型快照版。匯出使用者提示、委派 prompt 及完整可見文字回覆；不匯出內部推理、系統／開發者指令或憑證。低層工具參數部分以受保護格式存於 session，不將不可讀內容誤列為 prompt。測試及 CI 原始工具輸出已另存 evidence/，程式、測試列印本與完整 Git 歷史保留實際編輯結果。

這是截至 manifest 中時間的完整工作對話快照；打包後的交付連結訊息不參與程式生成。所有本次使用的 prompt 及使用者審查回覆均在快照中。
""", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
