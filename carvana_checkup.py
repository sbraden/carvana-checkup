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

    def search(self):
        data = json.dumps({
            'BodyStyle': [],
            'Color': [],
            'DownPayment': None,
            'DriveTrain': [],
            'Features': None,
            'FilterToExclude': None,
            'MileageMax': None,
            'Models': 'a_',
            'MonthlyPayment': None,
            'Page': 1,
            'PriceMax': None,
            'PriceMin': None,
            'SortBy': "Newest",
            'YearMax': 2014,
            'YearMin': 2012,
        })

        response = requests.post(
            self.search_url,
            headers=self.search_headers,
            data=data)

        response.raise_for_status()
        return response.json()['results']


def main():

    carvana = Carvana()
    results = carvana.search()

    print 'Number of results:', len(results)

    for result in results:
        print result['StockNumber']

if __name__ == '__main__':
    main()
