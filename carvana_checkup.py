import sys
import shelve
import json
import smtplib
import requests
import yaml
from email.mime.text import MIMEText


class Carvana(object):
    search_url = 'http://www.carvana.com/search/runsearch'
    search_headers = {
        'Content-Type': 'application/json'
    }

    def search(self, model, year_min=None, year_max=None):
        data = json.dumps({
            'Color': [],
            'DownPayment': None,
            'DriveTrain': [],
            'Features': None,
            'FilterToExclude': None,
            'MileageMax': None,
            'Models': model,
            'MonthlyPayment': None,
            'Page': 1,
            'PriceMax': None,
            'PriceMin': None,
            'SortBy': 'Newest',
            'YearMax': year_max,
            'YearMin': year_min,
        })

        response = requests.post(
            self.search_url,
            headers=self.search_headers,
            data=data
        )

        response.raise_for_status()
        return response.json()['results']


class Mailer(object):
    def __init__(self, host, port, ssl, username, password):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.username = username
        self.password = password

    def connect(self):
        if self.ssl:
            self.server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            self.server = smtplib.SMTP(self.host, self.port)

        self.server.login(self.username, self.password)

    def send(self, to_addrs, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.username
        msg['To'] = to_addrs
        self.server.sendmail(self.username, to_addrs, msg.as_string())

    def quit(self):
        self.server.quit()


def get_pk(car):
    return str(car['StockNumber'])


def render_subject(cars):
    return 'Found %d new cars!' % len(cars)


def render_body(cars):
    lines = []
    line = '{Make} {Model} {Year} {TrimLine2} {Mileage}mi {FormattedPrice}'

    for car in cars:
        lines.append(line.format(**car))

    lines = '\n'.join(lines)
    print lines

    return lines


def send_notification(config, cars):
    if not cars:
        return

    mailer = Mailer(**config['email'])
    subject = render_subject(cars)
    body = render_body(cars)

    mailer.connect()
    mailer.send(config['notifiy_email'], subject, body)
    mailer.quit()


def main(config):
    carvana = Carvana()
    db = shelve.open(config['database'])

    cars = carvana.search(**config['search'])
    new_cars = [c for c in cars if get_pk(c) not in db]

    print 'Found', len(cars), 'total cars.'
    print 'Found', len(new_cars), 'new cars.'
    send_notification(config, new_cars)

    for car in cars:
        db[get_pk(car)] = car

    db.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s <config>' % sys.argv[0]
        sys.exit(1)

    with open(sys.argv[1]) as fp:
        main(yaml.load(fp))
