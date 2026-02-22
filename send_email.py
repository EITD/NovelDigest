import os
import sys
import json
import argparse
from dotenv import load_dotenv
import yagmail
from novel import load_data

if os.path.exists("config.env"):
    try:
        load_dotenv("config.env", override=False)
    except TypeError:
        load_dotenv("config.env")

novels = load_data()  # Dict[str, Novel]

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
    parser.add_argument("--dry-run", action="store_true", help="print the email body instead of sending")
    args = parser.parse_args()

    sections_text = []
    sections_html = []

    for t in types:
        # look for selected files inside the type directory first
        type_dir = str(t)
        found = []
        if os.path.isdir(type_dir):
            for fname in sorted(os.listdir(type_dir)):
                fpath = os.path.join(type_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                if fname.startswith("selected") and fname.endswith(".json"):
                    found.append(os.path.join(type_dir, fname))

        for path in found:
            books = load_novels(path)
            if not books:
                continue
            basename = os.path.splitext(os.path.basename(path))[0]
            title = f"{t} {basename}"
            sections_text.append(format_text(books, title=title))
            sections_html.append(format_html(books, title=title))

    combined_text = "\n\n".join(sections_text)
    # join HTML sections with a horizontal rule
    combined_html = "<hr/>".join(sections_html)

    smtp_user = os.getenv("QQ_EMAIL")
    smtp_pass = os.getenv("QQ_PASS")

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
    main(novels.keys())
