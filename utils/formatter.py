import os

from exchangelib import Mailbox, Message, FileAttachment


# Функция создания папки для файлов юзеров
def make_folder(user_id):
    os.mkdir('data/' + str(user_id))


# Функция формирования почтового отправления
def send_email(accounts, subject, body, emails, attachments):
    to_recipients = []
    for email in emails:
        to_recipients.append(Mailbox(email_address=email))
    # Create message
    m = Message(account=accounts,
                folder=accounts.sent,
                subject=subject,
                body=body,
                to_recipients=to_recipients)
    # attach files
    for name in attachments:
        with open(name, 'rb') as f:
            content = f.read()
        file = FileAttachment(name=name, content=content)
        os.remove(name)
        m.attach(file)
    m.send_and_save()
