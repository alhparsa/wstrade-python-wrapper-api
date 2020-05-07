from typing import *
import requests
import json


class WSTrade():
    def __init__(self, email: str, password: str):
        self._login(email, password)
        self.accounts = []
        self.getAccountID()

    def _login(self, email: str, password: str):
        """
        Given an email and passowrd, it will initiate a connection
        with the wealthsimple server to gather the neccessary tokens
        for establishing connections in the future.
        """
        login_url = 'https://trade-service.wealthsimple.com/auth/login'
        content_type = {'Content-Type': 'application/json'}
        account_info = {'email': email,
                        'password': password}
        req = requests.post(
            url=login_url, json=account_info, headers=content_type)
        if '"error":"Not authorized"' in req.text:
            raise ConnectionError('Email or password is wrong')
        headers = req.headers
        self._access_token = headers['X-Access-Token']
        self._refresh_token = headers['X-Refresh-Token']
        self._header = {'Authorization': self._access_token}

    def getForex(self) -> dict:
        """
        Return the current exchange rate that WS Trade uses.
        """
        forex_url = 'https://trade-service.wealthsimple.com/forex'
        req = requests.get(forex_url, headers=self._header).text
        return json.loads(req)

    def _getAccountIDs(self) -> dict:
        """
        Return the accounts owned by the users on WS Trade.
        """
        accountsIDs_url = 'https://trade-service.wealthsimple.com/account/list'
        req = requests.get(accountsIDs_url, headers=self._header).text
        return json.loads(req)

    def getAccountID(self) -> list:
        """
        Returns a list of accounts owned by the user.
        """
        self.accounts = []
        try:
            js = self._getAccountIDs()['results']
            for account in js:
                temp = {}
                temp['AccountID'] = account['id']
                temp['Blanace'] = float(account['current_balance']['amount'])
                temp['BuyingPower'] = float(account['buying_power']['amount'])
                self.accounts.append(temp)
            return self.accounts
        except:
            raise ConnectionRefusedError('Connection issues, try to instantiate the \
                                          object again')

    # def get
    def _getSecurity(self, symbol: str) -> dict:

        query_url = "https://trade-service.wealthsimple.com/securities?query=" + symbol
        req = requests.get(query_url, headers=self._header).text
        return json.loads(req)

    def getSecurityId(self, symbol: str):
        """
        Given the ticker of a security it would return its security ID within the app.
        """
        try:
            res = self._getSecurity(symbol)['results']
            for item in res:
                if item['stock']['symbol'].lower() == symbol.lower():
                    return item['id']
        except:
            raise ConnectionRefusedError('Connection issues, try to instantiate the \
                                    object again')

    def _getQuote(self, sec_id: str) -> dict:
        query_url = "https://trade-service.wealthsimple.com/securities/" + sec_id
        req = requests.get(query_url, headers=self._header).text
        return json.loads(req)

    def getQuote(self, sec_id: str, last_price_forex_buy: bool = True, convert: bool = False) -> dict:
        """
        Given the security id, it would return its prices.
        If the security's currency is USD, it would automatically
        converts it into CAD. `last_price_forex_buy` asks the user
        to convert the last price with the forex buy rate or sell rate.
        """
        js_dic = self._getQuote(sec_id)
        currency = js_dic['currency']
        quote = js_dic['quote']
        res = {}
        res['ask'], res['bid'], res['price'] = float(
            quote['ask']), float(quote['bid']),\
            float(quote['amount'])

        if currency == 'USD' and convert:
            forex = self.getForex()['USD']
            buy_rate, sell_rate = forex['buy_rate'], forex['sell_rate']
            res['bid'] = (res['bid'] * buy_rate)
            res['ask'] = (res['ask'] * sell_rate)
            if last_price_forex_buy:
                res['price'] = (res['price']*buy_rate)
            else:
                res['price'] = (res['price']*sell_rate)
        return res

    def _placeOrder(self,
                    security_id: str,
                    order_type: str = 'buy_quantity',
                    sub_type: str = 'market',
                    account: str = None,
                    limit_price: float = 1,
                    quantity: int = 1):
        """
        Create an order based on the specifications.
        """
        if account == None:
            account = self.accounts[0]['AccountID']
        if order_type == "sell_quantity" and sub_type == "market":
            order_dict = {
                "account_id": account,
                "quantity": quantity,
                "security_id": security_id,
                "order_type": order_type,
                "order_sub_type": sub_type,
                "time_in_force": "day",
            }
        else:
            order_dict = {
                "account_id": account,
                "quantity": quantity,
                "security_id": security_id,
                "order_type": order_type,
                "order_sub_type": sub_type,
                "time_in_force": "day",
                "limit_price": limit_price
            }
        order_url = "https://trade-service.wealthsimple.com/orders"
        req = requests.post(order_url, headers=self._header,
                            json=order_dict).text
        return json.loads(req)

    def buyLimitOrder(self, security_id, limit_price, account_id=None, quantity=1):
        if account_id == None:
            account_id = self.accounts[0]['AccountID']
        res = self._placeOrder(security_id, 'buy_quantity',
                               'limit', account_id, limit_price, quantity)
        return res

    def buyMarketOrder(self, security_id, limit_price=1, account_id=None, quantity=1):
        if account_id == None:
            account_id = self.accounts[0]['AccountID']
        res = self._placeOrder(security_id, 'buy_quantity',
                               'market', account_id, limit_price, quantity)
        return res

    def sellLimitOrder(self, security_id, limit_price, account_id=None, quantity=1):
        if account_id == None:
            account_id = self.accounts[0]['AccountID']
        res = self._placeOrder(security_id, 'sell_quantity',
                               'limit', account_id, limit_price, quantity)
        return res

    def sellMarketOrder(self, security_id, account_id=None, quantity=1):
        if account_id == None:
            account_id = self.accounts[0]['AccountID']
        res = self._placeOrder(security_id, 'sell_quantity',
                               'market', account_id, quantity=quantity)
        return res

    def _getOrderHistory(self, account_id):
        """
        Returns all the orders submitted by this account
        """
        order_url = "https://trade-service.wealthsimple.com/orders/?account="
        req = requests.get(order_url, headers=self._header).text
        return json.loads(req)

    def getOrderHistory(self) -> dict:
        """
        Returns all the orders submitted by this account
        """

        return self._getOrderHistory()

    def getPendingOrders(self) -> dict:
        """
        Returns all the pending orders submitted by this account
        """
        orders = self.getOrderHistory()
        res = []
        for order in orders:
            if order['filled_at'] == None and order['status'] != 'cancelled':
                res.append(order)
        return res

    def getCancelledOrders(self) -> dict:
        """
        Returns all the cancelled orders submitted by this account
        """
        orders = self.getOrderHistory()
        res = []
        for order in orders:
            if order['status'] == 'cancelled':
                res.append(order)
        return res

    def getFilledOrders(self) -> dict:
        """
        Returns all the filled orders submitted by this account
        """
        orders = self.getOrderHistory()
        res = []
        for order in orders:
            if order['status'] == 'posted':
                res.append(order)
        return res

    def _cancelOrder(self, order_id):
        order_url = f'https://trade-service.wealthsimple.com/{order_id}'
        res = requests.delete(order_url, headers=self._header).text
        return res

    def cancelOrder(self, order_id):
        """
        Given an order id, it will cancel the order
        """
        res = self._cancelOrder(order_id)
        return res
