from flask import Flask, render_template, request
import joblib
import socket
import re
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import time

# Gmail IMAP settings
IMAP_SERVER = 'imap.gmail.com'
PORT = 993  # SSL/TLS port

# Your Gmail credentials
EMAIL = '' 
PASSWORD = '' 

# File paths
MODEL_FILE = 'model/phishing-model.joblib'  # Path to the trained model file
TFIDF_VECTORIZER_FILE = 'model/tfidf-vectorizer.joblib'  # Path to the fitted TfidfVectorizer

# Create the Flask application
app = Flask(__name__)

# Load the trained phishing model
model = joblib.load(MODEL_FILE)

# Load the fitted TfidfVectorizer instance
feature_extraction = joblib.load(TFIDF_VECTORIZER_FILE)

# Function to extract URLs from email body
def extract_urls(body):
    url_regex = r'(https?://[^\s]+)'
    urls = re.findall(url_regex, body)
    return urls

# Function to resolve URL to IP address
def resolve_url_to_ip(urls):
    url_ip_dict = {}
    for url in urls:
        try:
            # Resolve URL to its IP address
            ip_address = socket.gethostbyname(url.split("//")[-1].split('/')[0])
            url_ip_dict[url] = ip_address
        except socket.gaierror:
            # Handle exceptions if the URL cannot be resolved
            url_ip_dict[url] = None
    return url_ip_dict

# Function to fetch, classify, and notify about new emails
def fetch_classify_new_emails():
    # Establish an SSL connection to Gmail's IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    
    # Log in with your Gmail credentials
    try:
        mail.login(EMAIL, PASSWORD)
    except imaplib.IMAP4.error as e:
        return f'Login failed: {e}'
    
    # Select the inbox
    mail.select("inbox")

    # Search for unread emails received since a specific date
    since_date = (datetime.now() - timedelta(minutes=1)).strftime('%d-%b-%Y')
    result, data = mail.search(None, f'(SINCE "{since_date}") (UNSEEN)')
    
    # Get the list of email IDs
    email_ids = data[0].split()
    
    email_results = []
    
    # Loop through each new, unread email
    for email_id in email_ids:
        # Fetch the email
        result, data = mail.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        # Decode the subject
        subject, encoding = decode_header(email_message["Subject"])[0]
        if encoding is not None:
            subject = subject.decode(encoding)
        
        # Get the sender
        sender = email_message.get("From")
        
        # Get the body of the email
        body = ''
        if email_message.is_multipart():
            # If the email is multipart, iterate over the parts to find the text part
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', 'ignore')
                    break
        else:
            # If the email is not multipart, the payload is the body
            body = email_message.get_payload(decode=True).decode('utf-8', 'ignore')
        
        # Extract URLs from the email body
        urls = extract_urls(body)
        
        # Resolve each URL to its IP address
        url_ip_dict = resolve_url_to_ip(urls)
        
        # Use the phishing model to classify the email
        input_data_features = feature_extraction.transform([f"{subject} {body}"])
        prediction = model.predict(input_data_features)
        
        # Determine whether the email is safe or phishing
        if prediction[0] == 1:
            email_results.append({
                'text': f"Spam Email Detected! From: {sender}, Subject: {subject}",
                'type': 'phishing',
                'urls': url_ip_dict
            })
        else:
            email_results.append({
                'text': f"Safe Email Received! From: {sender}, Subject: {subject}",
                'type': 'safe',
                'urls': url_ip_dict
            })

        # Remove the \Seen flag to leave the email unread
        mail.store(email_id, '-FLAGS', '\\Seen')
    
    # Logout and close the connection
    mail.logout()

    return email_results

# Flask route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        email_results = fetch_classify_new_emails()
        return render_template('index.html', email_results=email_results)
    
    return render_template('index.html')

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
