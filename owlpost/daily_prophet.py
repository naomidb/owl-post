from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
import smtplib
import getpass

def connect_to_smtp(host, port):
    try:
        connection = smtplib.SMTP(host=host,
                                  port=port,)
        connection.starttls()
        login = input("Enter your gatorlink: ")
        password = getpass.getpass("Enter your password: ")
        connection.login(login, password)
    except smtplib.SMTPConnectError as e:
        print(e)
        connection = None

    return connection

def create_file(log, filename):
    message = ''
    message += '''\
                <!DOCTYPE html>\
                <html>\
                <head>\
                    <title>VIVO Uploads</title>\
                </head>\
                <body>'''
    if len(log.articles) > 0:
        message += '<h2>New Publications: ' + str(len(log.articles)) + '</h2>'
        for pub in log.articles:
            message += '<p>' + pub[0] + '  -- <a href="' + pub[1] + '" target="_blank">VIVO Entry</a></p>'
        message += '<br>'
    if len(log.authors) > 0:
        message += '<h2>New People: ' + str(len(log.articles)) + '</h2>'
        for person in log.authors:
            message += '<p>' + person[0] + '  -- <a href="' + person[1] + '" target="_blank">VIVO Entry</a></p>'
        message += '<br>'
    if len(log.publishers) > 0:
        message += '<h2>New Publishers: ' + str(len(log.articles)) + '</h2>'
        for publisher in log.publishers:
            message += '<p>' + publisher[0] + '  -- <a href="' + publisher[1] + '" target="_blank">VIVO Entry</a></p>'
        message += '<br>'
    if len(log.journals) > 0:
        message += '<h2>New Journals: ' + str(len(log.articles)) + '</h2>'
        for journal in log.journals:
            message += '<p>' + journal[0] + '  -- <a href="' + journal[1] + '" target="_blank">VIVO Entry</a></p>'
        message += '<br>'

    with open(filename, 'w') as msg:
        msg.write(message)

def create_email(log, config, file):
    body = '''
Hello UF VIVO Community,

{} publications have been added to VIVO. The publications are from the most recent import of data from Clarivate's Web of Science. The titles of the new publications are attached, along with new publishers, journals, and people.

Regards,
The CTSIT VIVO Team
\n\n
'''.format(str(len(log.articles)))

    msg = MIMEMultipart()
    msg['From'] = config.get('from_email')
    msg['Subject'] = config.get('subject')

    to_list = config.get('to_emails')
    to_string = ",".join(to_list)
    msg['To'] = to_string

    msg.attach(MIMEText(body, 'plain'))

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()

    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    return msg

def send_message(msg, connection, config):
    connection.sendmail(config.get('from_email'), config.get('to_emails'), msg.as_string())
    connection.quit()

