from flask import Flask, render_template, request, redirect, url_for, session, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Use environment variables

@app.route("/", methods=["GET", "POST"])
def user_email():
    if request.method == "POST":
        session['user_email'] = request.form['user_email']
        session['user_password'] = request.form['user_password']  # App password
        return redirect(url_for('recipients'))
    return render_template("user_email.html")

@app.route("/recipients", methods=["GET", "POST"])
def recipients():
    if request.method == "POST":
        session['recipients'] = request.form['recipients'].split(',')
        session['names'] = request.form['names'].split(',')
        return redirect(url_for('compose'))
    return render_template("recipients.html")

@app.route("/compose", methods=["GET", "POST"])
def compose():
    if request.method == "POST":
        subject = request.form['subject']
        body_template = request.form['body']

        for email, name in zip(session['recipients'], session['names']):
            personalized_body = body_template.replace("[NAME]", name.strip())
            if send_custom_email(email.strip(), subject, personalized_body):
                flash(f"Email sent successfully to {email}!", "success")
            else:
                flash(f"Failed to send email to {email}.", "danger")

        return redirect(url_for('user_email'))
    return render_template("compose.html")

def send_custom_email(to_email, subject, body):
    from_email = session['user_email']
    password = session['user_password']  # App password
    
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    app.run(debug=True)
