import smtplib
from email.message import EmailMessage
from pathlib import Path
import datetime
import os

email_user = os.environ.get("EMAIL_USER") #set in project "secrets"
email_pass = os.environ.get("EMAIL_PASS")

# Load file paths
today = datetime.date.today().isoformat()
TMT_brief_path = Path("api/static/assets/briefs") / f"TMT_Brief_{today}.pdf"
Energy_brief_path = Path("api/static/assets/briefs") / f"Energy_Brief_{today}.pdf"
TMT_raw_path = Path("api/static/assets/raw") / f"TMT_Brief_{today}_raw.txt"
Energy_raw_path = Path("api/static/assets/raw") / f"Energy_Brief_{today}_raw.txt"

msg = EmailMessage()
msg["Subject"] = f"TMT and energy Daily Brief – {today}"
msg["From"] = "lingcheng783@gmail.com" #put in your own email
msg["To"] = ["victorche0909@gmail.com", "jay_dong_0719@outlook.com"]

msg.set_content("Attached is the TMT brief and raw news summary for today.")

# Attach PDF
msg.add_attachment(TMT_brief_path.read_bytes(), maintype='application', subtype='pdf', filename=TMT_brief_path.name)
msg.add_attachment(Energy_brief_path.read_bytes(), maintype='application', subtype='pdf', filename=TMT_brief_path.name)

# Attach raw text
msg.add_attachment(TMT_raw_path.read_bytes(), maintype='text', subtype='plain', filename=TMT_raw_path.name)
msg.add_attachment(Energy_raw_path.read_bytes(), maintype='text', subtype='plain', filename=Energy_raw_path.name)

# Send email (Gmail example with app password)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(email_user, email_pass)
    smtp.send_message(msg)
