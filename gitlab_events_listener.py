from flask import Flask, request
import logging
import smtplib
from email.mime.text import MIMEText
import json

#Variables
#Change it on yours
mail_server = "mail.myserver.com:587"
email_sender = "email@myserver.com"
sender_email_password = "MY PASSWORD"
email_for_events = "events@mayserver.com"

app = Flask(__name__)

# Setup logging
logging.basicConfig(filename='events.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Make Mails look nice
def generate_html_table(data):
    html = '<table border="1" style="width:100%; border-collapse: collapse;">'
    html += '<tr><th>Key</th><th>Value</th></tr>'
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                html += f'<tr><td>{key}.{subkey}</td><td>{subvalue}</td></tr>'
        else:
            html += f'<tr><td>{key}</td><td>{value}</td></tr>'
    html += '</table>'
    return html


# Function to send email
def send_email(event_data):
    sender_email = email_sender
    recipient_email = email_for_events
    msg = MIMEText(event_data)
    msg = MIMEText(event_data,'html')
    #msg.attach(event_data)
    msg['Subject'] = "New Event Received"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Send the message via SMTP server. Set yours email server, pogin and password
    try:
        with smtplib.SMTP(mail_server) as server:
            server.login(email_sender, sender_email_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
    except Exception as e:
        logging.error('Failed to send email: %s', e)


# Endpoint to handle incoming events
@app.route('/events', methods=['POST'])
def event_listener():
    token = request.headers.get('X-Gitlab-Event-Streaming-Token')
    if token != 'XXXXXX': # SET YOURS!
        logging.warning('Forbidden: Invalid token')
        return 'Forbidden', 403
    print("Event arrived!")
    event_data = request.get_json()
    print("Event data : ", event_data)
    logging.info('Received event: %s', event_data)
    # Generate the HTML table
    html_table = generate_html_table(event_data)
    send_email(html_table)
    return '', 200


if __name__ == "__main__":
    app.run(port=5000)

