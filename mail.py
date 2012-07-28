import smtplib
import credentials

def sendMail(toaddrs, subject, msg):
    # Credentials (if needed)
    username = credentials.mail_user 
    password = credentials.mail_password 
    message = """From: Service <service@frikifriends.net>
To: %s 
Subject: %s 

%s
""" % ( ", ".join(toaddrs), subject, msg)

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(username, toaddrs, message)
    server.quit()

if __name__ == "__main__":
    sendMail(["kozko2001@gmail.com"], "SUBJECT" , "TEST?")
