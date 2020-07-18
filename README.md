# takeaway

Small python takeaway android api implementation + order history dumper

For takeaway.com/lieferando/thuisbezorgd/etc, but only tested with lieferando

Credit for the api reference to https://github.com/TakeawayAPI/

I do not intend to maintain this for anything but my use case (personal
budgeting), fork it and rename it if you want to make it into a general purpose
python API.

## Deps

* python 3.8
* lxml
* requests

## Usage

Create `takeaway_creds.py` with

    USERNAME = 'your@email.com'
    PASSWORD = 'hunter2'
    COUNTRY_CODE = 'DE'

Then run `python takeaway.py > order_history.json`

Default output is a json list with the full order history in a format that
seemed convenient for my personal use case:

    [
      {
        "id": "ORNQ7313551",
        "time": "2020-06-19T22:33:00",
        "details": {
          "total_amount": 36.5,
          "restaurant_name": "Call a Pizza",
          "products": [
            {
              "name": "Pizza Free-Style [SINGLE CA. 26CM] (Ananas, Mais)",
              "price": 8.3
            },
            {
              "name": "Kombiniere eine Pasta [Vollkorn-Penne] (Oliven, TABASCO, Mozzarella)",
              "price": 11.000000000000002
            },
            {
              "name": "8 Pizzabrötchen mit Edamer und Kräuterbutter",
              "price": 4.9
            },
            {
              "name": "Kombiniere eine Pasta [Vollkorn-Penne] (Ananas, Grande Gustoso, Bacon, Mozzarella)",
              "price": 12.300000000000002
            }
          ]
        }
      }
    ]

The python API is a bit more flexible, and it's easy enough to extend to more
upstream API endpoints, but I'm not doing that unless I personally need it.
