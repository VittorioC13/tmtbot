import smtplib
from email.message import EmailMessage
from pathlib import Path
import datetime
import os
import mimetypes

email_user = os.environ.get("EMAIL_USER") #set in project "secrets"
email_pass = os.environ.get("EMAIL_PASS")


# Load file paths
today = datetime.date.today().isoformat()
base_path = Path(__file__).resolve().parent.parent 
raw_dir = base_path / 'api' / "static" / "assets" / "raw"
brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'

TMT_brief_path = brief_dir / f"TMT_Brief_{today}.pdf"
TMT_raw_path = raw_dir / f"TMT_Brief_{today}_raw.txt"
Energy_brief_path = brief_dir / f"Energy_Brief_{today}.pdf"
Energy_raw_path = raw_dir / f"Energy_Brief_{today}_raw.txt"
Healthcare_brief_path = brief_dir / f"Healthcare_Brief_{today}.pdf"
Healthcare_raw_path = raw_dir / f"Healthcare_Brief_{today}_raw.txt"


attachments_paths = [TMT_brief_path, TMT_raw_path, Energy_brief_path, Energy_raw_path, Healthcare_brief_path, Healthcare_raw_path]


def send_emails():
    msg = EmailMessage()
    msg["Subject"] = f"TMT and energy Daily Brief – {today}"
    msg["From"] = "lingcheng783@gmail.com" #put in your own email
    msg["To"] = ["victorche0909@gmail.com", "jay_dong_0719@outlook.com", "lingchao@arts-united.cn", "linghucun@126.com"] #contacts to send emails to
    #msg["To"] = ["lingcheng783@gmail.com"]

    msg.set_content("Attached is the TMT brief and raw news summary for today.")
    print("Attaching files to email...")
    for attachment in attachments_paths:
        if not attachment.exists():
            print(f"Warning: File not found: {attachment}")
            continue

        ctype, encoding = mimetypes.guess_type(attachment.name)
        if ctype is None or encoding is None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        msg.add_attachment(
            attachment.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=attachment.name
        )
        print(f"✓ Attached {attachment.name}")


    # Send email (Gmail example with app password)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        #smtp.login(email_user, email_pass)
        smtp.login(email_user, email_pass)
        smtp.send_message(msg)




