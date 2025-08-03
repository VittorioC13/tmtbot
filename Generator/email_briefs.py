import smtplib
from email.message import EmailMessage
from pathlib import Path
import datetime
import os

#email_user = os.environ.get("EMAIL_USER") #set in project "secrets"
#email_pass = os.environ.get("EMAIL_PASS")

def send_emails():
    # Load file paths
    today = datetime.date.today().isoformat()
    base_path = Path(__file__).resolve().parent.parent 
    raw_dir = base_path / 'api' / "static" / "assets" / "raw"
    brief_dir = base_path / 'api' / 'static' / 'assets' / 'briefs'


    TMT_brief_path = brief_dir / f"TMT_Brief_{today}.pdf"
    Energy_brief_path = brief_dir / f"Energy_Brief_{today}.pdf"
    TMT_raw_path = raw_dir / f"TMT_Brief_{today}_raw.txt"
    Energy_raw_path = raw_dir / f"Energy_Brief_{today}_raw.txt"
    

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
        #smtp.login(email_user, email_pass)
        smtp.login("lingcheng783@gmail.com", "pjcxrxbdzrnvonur")
        smtp.send_message(msg)


