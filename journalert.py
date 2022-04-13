import time
from datetime import date, datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import path
import feedparser as fp
import config

latest_entries = dict.fromkeys(config.no_pubdate, None)

# latest.tsv holds information about the latest entry in feeds without pubDate
if path.exists("latest.tsv"):
    with open("latest.tsv", "r") as f:
        for line in f:
            fields = line.rstrip().split("\t")
            latest_entries[fields[0]] = fields[1]

new_latest_entries = latest_entries

now = time.mktime(time.localtime())

out_lines = []
plain_lines = []

for feed in config.feeds:
    f = fp.parse(feed)
    new_entries = []

    if feed not in latest_entries.keys():
        latest_utime = None
        for e in reversed(f['entries']):
            upd_time = time.mktime(e["updated_parsed"]) if e["updated_parsed"] else latest_utime
            daydiff = (now - upd_time)/86400
            if daydiff <= 1:
                new_entries.append(e)
            latest_utime = upd_time
    else:
        # For feeds without pubDate
        for e in f['entries']:
            if e["link"] != latest_entries[feed]:
                new_entries.insert(0, e)
                new_latest_entries[feed] = new_entries[-1]["link"]
            else:
                break

    if new_entries:
        out_lines.append(f"<h4>{f['feed']['title']}</h4>")
        out_lines.append("<ul>")
        plain_lines.append(f"# {f['feed']['title']}")
        plain_lines.append("")
        for e in new_entries:
            out_lines.append(f"<li><a href={e['link']}>{e['title']}</a></li>")
            plain_lines.append(f"* {e['title']} ({e['link']})")
        out_lines.append("</ul>")
        plain_lines.append("")

# Update checklist of feeds without pubDate
checklist_lines = []
for url, latest in new_latest_entries.items():
    checklist_lines.append(f"{url}\t{latest}\n")

with open("latest.tsv", "w") as f:
    f.writelines(checklist_lines)

journal_count = len([l for l in out_lines if l.startswith("<h4>")])

if journal_count > 0:
    out_lines.insert(0, "<html><head><style>ul li{margin-bottom:1em;}</style></head><body>")
    out_lines.insert(1, f"<p>Hello! {journal_count} journal{'s' if journal_count > 1 else ''} have published new articles in the last 24 hours:</p>")
    out_lines.append("</body></html>")

    plain_lines.insert(0, f"Hello! {journal_count} journal{'s' if journal_count > 1 else ''} have published new articles in the last 24 hours:")
    plain_lines.insert(1, "")

    html = "\n".join(out_lines)
    text = "\n".join(plain_lines)

    sender_email = config.sender_email
    password = config.password
    receiver_email = config.receiver_email

    message = MIMEMultipart("alternative")
    message["Subject"] = f"New articles for {date.today().strftime('%B %d, %Y')}"
    message["From"] = f"Journalert <{sender_email}>"
    message["To"] = receiver_email
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
