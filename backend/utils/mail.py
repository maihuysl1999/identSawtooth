# https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development

# import smtplib, ssl

# port = 465  # For SSL
# smtp_server = "smtp.gmail.com"
# sender_email = "testForCode712@gmail.com"  # Enter your address
# receiver_email = "dothechuyen2101@gmail.com"  # Enter receiver address
# password = input("Type your password and press enter: ")
# message = """\
# Subject: Test

# This message is sent from Python."""

# context = ssl.create_default_context()
# with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, message)

# ------------------------------------------------------------------------------------------------------

# import smtplib, ssl

# port = 587  # For starttls
# smtp_server = "smtp.gmail.com"
# sender_email = "testForCode712@gmail.com"
# receiver_email = "dothechuyen2101@gmail.com"
# password = input("Type your password and press enter:")
# message = """\
# Subject: Hi there

# This message is sent from Python."""

# context = ssl.create_default_context()
# with smtplib.SMTP(smtp_server, port) as server:
#     server.ehlo()  # Can be omitted
#     server.starttls(context=context)
#     server.ehlo()  # Can be omitted
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, message)

# ----------------------------------------------------------------------------------------------------------

# def send_email(user, pwd, recipient, subject, body):
#     import smtplib

#     FROM = user
#     TO = recipient if isinstance(recipient, list) else [recipient]
#     SUBJECT = subject
#     TEXT = body

#     # Prepare actual message
#     message = """From: %s\nTo: %s\nSubject: %s\n\n%s
#     """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.ehlo()
#         server.starttls()
#         server.login(user, pwd)
#         server.sendmail(FROM, TO, message)
#         server.close()
#         print('successfully sent the mail')
#     except:
#         print("failed to send mail")
# send_email('testForCode712@gmail.com','Chuyen92351',"a@a.com","HIhihi","test ty thoi")

# -------------------------------------------------------------------------------------------------------------------


def otp_code():
    import random, string
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return x
def send_email(recipient,subject ,user,otp):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    # password = input("Type your password and press enter:")
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Your {subject} has been changed!!!"
    sender= "vchaincdct@gmail.com"
    pwd="vchain_v2"
    message["To"] = recipient
    user_id=user["user_id"]
  
    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    html=open("utils/index.txt","r").read()
    if otp!="":
        html=html.split("{2}")[0]+"This is OTP code for verify:"+html.split("{2}")[1]
    else:
        html=html.split("{2}")[0]+html.split("{2}")[1]
    html=html.split("{0}")[0]+otp+html.split("{0}")[1]
    html=html.split("{1}")[0]+subject+html.split("{1}")[1]
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)
    # verify=verifyEmail(receiver_email)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, recipient, message.as_string())
        server.close()
        print('successfully sent the mail')
    except Exception as e:
        print("failed to send mail",e)

# send_email("testForCode712@gmail.com","Chuyen92351","dothechuyen2101@gmail.com","hihihi")
