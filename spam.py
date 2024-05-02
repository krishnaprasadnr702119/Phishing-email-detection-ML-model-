import imaplib
import email
from email.header import decode_header

# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'
PORT = 993  # SSL/TLS port

# Your Gmail credentials
  
EMAIL = '' 
PASSWORD = '' 

# Establish an SSL connection to Gmail's IMAP server
mail = imaplib.IMAP4_SSL(IMAP_SERVER) # , PORT
print(mail)

# Log in with your Gmail credentials
try:
    mail.login(EMAIL, PASSWORD)
    print('Login successful!')
except imaplib.IMAP4.error as e:
    print('Login failed:', e)

# Select the inbox
mail.select("inbox")

# Search for all emails in the inbox
result, data = mail.search(None, "ALL")

# print(result,data)

# Get the list of email IDs
email_ids = data[0].split()

# Loop through each email
for email_id in email_ids:
    # Fetch the email by ID
    result, data = mail.fetch(email_id, "(RFC822)")
    # print(result, data)
    
    # Parse the email content
    raw_email = data[0][1]
    email_message = email.message_from_bytes(raw_email)
    # print(email_message)
    
    # Get the email subject and sender
    subject, encoding = decode_header(email_message["Subject"])[0]
    if encoding is not None:
        subject = subject.decode(encoding)
    sender = email_message.get("From")
    
    # Print the subject and sender
    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print("-" * 40)

# Logout and close the connection
mail.logout()