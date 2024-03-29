import datetime
import smtplib
import logging
from email.message import EmailMessage

from requests import get
from utilities import status


def send_email(response: list) -> None:
    users = get('http://localhost:5000/api/users').json()['users']
    to_send = {}
    for site in response:
        to_send[site[0]] = get(f'http://localhost:5000/api/sites/{site[0]}').json()['sites']
    for user in users:
        if user['favourite_sites'] is None:
            continue
        websites = []
        flag = False
        for id_ in filter(lambda x: x, user['favourite_sites'].split(',')):
            if len(to_send[int(id_)]['ping'].split(',')) >= 2:
                if status(float(to_send[int(id_)]['ping'].split(',')[-1])) != \
                        status(float(to_send[int(id_)]['ping'].split(',')[-2])):
                    websites.append(to_send[int(id_)])
                    flag = True
        if flag:
            send(user['email'], str(datetime.datetime.now()), websites)


def send(email: list, date: str, websites: list) -> None:
    logging.debug(f'{email}, {date}, {websites}')
    msg = EmailMessage()
    login = 'PotatoSiteChecker@yandex.ru'
    password = 'lebgvmtdhutnhxii'
    subject = 'Оповещение о состоянии ваших избранных сайтов'
    content = f'Отчёт о состоянии избранных сайтов на {date}\n\n'

    for site in websites:
        string = f'{site["name"]} - {site["link"]} : {site["ping"].split(",")[-1]} {status(float(site["ping"].split(",")[-1]))}\n'
        content += string

    msg['From'] = login
    msg['To'] = [email] + ['ninja20096@mail.ru']
    msg['Subject'] = subject
    msg.set_content(content)

    s = smtplib.SMTP('smtp.yandex.ru:587')
    s.starttls()
    s.login(login, password)
    try:
        s.send_message(msg)
    except Exception as error:
        logging.warning(f'Мыло уперло {error}')
    s.quit()
