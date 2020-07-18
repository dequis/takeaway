#!/usr/bin/env python

import json
import datetime
import requests
import hashlib
import lxml.etree

from takeaway_creds import USERNAME, PASSWORD, COUNTRY_CODE

CONST_VARS = {
    'version': 5.7,
    'systemversion': 24,
    'appname': 'Takeaway.com',
    'language': 'en',
}

URL = 'https://citymeal.com/android/android.php'
SECRET = '4ndro1d'


def to_vars(*args):
    return {f'var{k}': v for k, v in enumerate(args, start=1)}

def gen_postdata(*args):
    signature_values = ''.join([str(x) for x in args])
    signature = hashlib.md5((signature_values + SECRET).encode()).hexdigest()
    return {
        'var0': signature,
        **to_vars(*args),
        **CONST_VARS,
    }

def pretty_tree(tree):
    return lxml.etree.tostring(tree, pretty_print=True).decode()

def parse_order_details(tree):
    output = {}
    output['total_amount'] = float(tree.find("tt").text)
    output['restaurant_name'] = tree.find("nm").text
    output['products'] = []

    seen_prices = 0
    for product in tree.findall("pr"):
        out_row = {}
        name = product.find("nm").text
        price = float(product.find("pc").text)

        extras = []
        for subproduct in product.findall("sd"):
            subprice = float(subproduct.find("pc").text)
            subname = subproduct.find("nm").text
            if subprice:
                price += subprice
                extras.append(subname)

        if extras:
            name += f' ({", ".join(extras)})'

        out_row['name'] = name
        out_row['price'] = price
        seen_prices += price

        output['products'].append(out_row)

    remainder = output['total_amount'] - seen_prices
    if abs(remainder) >= 0.01:
        output['remainder'] = round(remainder, 2)

    return output

def parse_time(time_string):
    return datetime.datetime.strptime(time_string, "%d-%m-%Y %H:%M")


class TakeawaySession:
    def __init__(self):
        self.session = requests.session()
        self.username = ''
        self.ic = ''
        self.sc = ''
        self.user_id = ''

    def request(self, *args):
        response = self.session.post(URL, data=gen_postdata(*args))
        response.raise_for_status()
        if response.text.startswith('<'):
            return lxml.etree.fromstring(response.text.encode())
        else:
            return response

    # API wrappers

    def request_getcountriesdata(self):
        return self.request('getcountriesdata')

    def request_userauth(self, username, password):
        # userauth(userName, userCredentials, countryCode, clientId, siteCode,
        #          (1, socialType, socialToken) | (0, '', ''))
        return self.request('userauth', username, password, self.ic, '',
            self.sc)

    def request_getorderhistory(self, page):
        # getorderhistory((email, clientId) | (userName, userCredentials),
        #                 countryCode, page, siteCode, isLoggedIn)
        return self.request('getorderhistory', self.username, self.user_id,
            self.ic, page, self.sc, 1)

    def request_getorderdetails(self, order_id):
        # getorderdetails((email, clientId) | (userName, userCredentials),
        #                 countryCode, orderId, siteCode, isLoggedIn)
        return self.request('getorderdetails', self.username, self.user_id,
            self.ic, order_id, self.sc, 1)


    # higher level functions

    def login(self, username, password, country_code):
        tree = self.request_getcountriesdata()
        country = tree.xpath("cd[cy/text() = '%s']" % country_code)[0]
        self.ic = country.find("ic").text
        self.sc = country.find("sc").text

        tree = self.request_userauth(username, password)

        self.user_id = tree.find("id").text
        self.username = username

    def get_order_history(self, page=0):
        tree = self.request_getorderhistory(page)

        orders = []
        for order in tree.findall("or"):
            out_order = {}
            out_order['id'] = order.find("id").text
            out_order['time'] = parse_time(order.find("ot").text).isoformat()

            details_tree = self.request_getorderdetails(out_order['id'])

            out_order['details'] = parse_order_details(details_tree)
            orders.append(out_order)

        return orders

    def get_full_order_history(self):
        page = -1
        while orders_page := self.get_order_history(page := page + 1):
            yield from orders_page

def main():
    takeaway = TakeawaySession()
    takeaway.login(USERNAME, PASSWORD, COUNTRY_CODE)
    print(json.dumps(list(takeaway.get_full_order_history())))

if __name__ == '__main__':
    main()
