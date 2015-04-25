import shelve
import json
import requests

# TODO: how to do notifications?

MODEL = 'a_'


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


def get_pk(car):
    return str(car['StockNumber'])


def main():
    carvana = Carvana()
    db = shelve.open('carvana.db')

    cars = carvana.search(MODEL)
    new_cars = [c for c in cars if get_pk(c) not in db]

    print 'Found', len(cars), 'total cars.'
    print 'Found', len(new_cars), 'new cars.'

    for car in new_cars:
        make = car['Make']
        model = car['Model']
        year = car['Year']
        mileage = str(car['Mileage']) + 'mi'
        price = car['FormattedPrice']

        print make, model, year, mileage, price

    for car in cars:
        db[get_pk(car)] = car

    db.close()


if __name__ == '__main__':
    main()
