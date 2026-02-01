#!/usr/bin/env python3
"""Send gb_novels.json via QQ mail using yagmail.

Requirements:
  pip install yagmail

Usage:
  Dry-run (print body):
    python3 send_gb_novels_email.py --dry-run

  Send to QQ mailbox (set env or use --to):
    export SMTP_USER=your_qq_email@qq.com
    export SMTP_PASS=your_qq_smtp_app_password
    python3 send_gb_novels_email.py --to recipient@qq.com --subject "GB Novels"
"""
import os
import sys
import json
import argparse
from dotenv import load_dotenv

try:
    import yagmail
except Exception:
    yagmail = None


def load_novels(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_text(novels, title):
    lines = [title, ""]
    for i, n in enumerate(novels, 1):
        t = n.get("title", "(no title)")
        a = n.get("author", "(unknown)")
        intro = n.get("intro", "")
        lines.append(f"{i}. {t} — {a}")
        if intro:
            lines.append(f"   {intro}")
    return "\n".join(lines)


def format_html(novels, title):
    parts = [f"<h3>{title}</h3>"]
    parts.append("<ul>")
    for i, n in enumerate(novels, 1):
        t = n.get("title", "(no title)")
        a = n.get("author", "(unknown)")
        intro = n.get("intro", "")
        item = f"<li><strong>{i}. {t}</strong> — <em>{a}</em>"
        if intro:
            item += f"<div style=\"margin-top:4px;\">{intro}</div>"
        item += "</li>"
        parts.append(item)
    parts.append("</ul>")
    return "\n".join(parts)


def send_via_yagmail(user, password, text_body, html_body):
    if yagmail is None:
        raise RuntimeError("yagmail is not installed. Run: pip install yagmail")
    # Use QQ SMTP server with SSL (port 465)
    yag = yagmail.SMTP(user=user, password=password, host='smtp.qq.com', smtp_ssl=True)
    contents = [text_body, html_body]
    yag.send(subject="Novels Update", contents=contents)
    yag.close()


def main(types):
    parser = argparse.ArgumentParser()
    # parser.add_argument("--to", help="recipient email address")
    # parser.add_argument("--subject", default="GB Novels Update")
    # parser.add_argument("--json", default="gb_novels.json", help="path to gb_novels.json")
    parser.add_argument("--dry-run", action="store_true", help="print the email body instead of sending")
    args = parser.parse_args()

    types = [t.strip() for t in types.split(",") if t.strip()]
    sections_text = []
    sections_html = []

    for t in types:
        path = f"selected_novels_{t}.json"
        if not os.path.exists(path):
            continue
        novels = load_novels(path)
        title = f"{t.upper()} Novels"
        sections_text.append(format_text(novels, title=title))
        sections_html.append(format_html(novels, title=title))

    if not sections_text:
        print("No selected_novels_{type}.json files found for types:", types, file=sys.stderr)
        sys.exit(1)

    combined_text = "\n\n".join(sections_text)
    # join HTML sections with a horizontal rule
    combined_html = "<hr/>".join(sections_html)

    load_dotenv("config.env")
    smtp_user = os.environ.get("QQ_EMAIL")
    smtp_pass = os.environ.get("QQ_PASS")

    if args.dry_run:
        print("--- Plain text ---\n")
        print(combined_text)
        print("\n--- HTML ---\n")
        print(combined_html)
        return

    if not all([smtp_user, smtp_pass]):
        print("Missing QQ SMTP settings. Set QQ_EMAIL and QQ_PASS (QQ app password) in config.env", file=sys.stderr)
        sys.exit(2)

    send_via_yagmail(smtp_user, smtp_pass, combined_text, combined_html)
    print("Email sent.")

if __name__ == "__main__":
    main(["gb", "mq"])