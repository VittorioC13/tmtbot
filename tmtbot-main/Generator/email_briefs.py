import smtplib
from email.message import EmailMessage
from pathlib import Path
import datetime
import os
import mimetypes

#email_user = os.environ.get("EMAIL_USER") #set in project "secrets"
#email_pass = os.environ.get("EMAIL_PASS")
region_list = ["US", "Europe"]

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

attachments_paths = []

for region in region_list:
    TMT_brief_path = brief_dir / f"{region}_TMT_Brief_{today}.pdf"
    Energy_brief_path = brief_dir / f"{region}_Energy_Brief_{today}.pdf"
    Healthcare_brief_path = brief_dir / f"{region}_Healthcare_Brief_{today}.pdf"
    Consumer_brief_path = brief_dir / f"{region}_Consumer_{today}.pdf"
    Industry_brief_path = brief_dir / f"{region}_Industry_{today}.pdf"
    attachments_paths.append(TMT_brief_path)
    attachments_paths.append(Energy_brief_path)
    attachments_paths.append(Healthcare_brief_path)

def send_emails():
    msg = EmailMessage()
    msg["Subject"] = f"TMT and energy Daily Brief – {today}"
    msg["From"] = "lingcheng783@gmail.com" #put in your own email
    msg["To"] = ["lingchao@arts-united.cn", "linghucun@126.com"]
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
    print("connecting to SMTP SSL...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        print("✓ connected")
        #smtp.login(email_user, email_pass)
        print("logging in...")
        smtp.login("lingcheng783@gmail.com", "pjcxrxbdzrnvonur")
        print("✓ logged in")
        print("sending email...")
        smtp.send_message(msg)
        
        

if __name__ == "__main__":
    send_emails()
    print("✓ emails sent")


