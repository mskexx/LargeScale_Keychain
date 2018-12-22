"""
KeyChain key-value store (stub).

NB: Feel free to extend or modify.
"""

import requests
from keychain.api_app import app
from threading import Thread
import time

class Callback:
    def __init__(self, transaction, app):
        self._transaction = transaction
        self._app = app

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        while not self.completed():
            time.sleep(4)
            break #Break or return?-


    def completed(self):
        """Polls the blockchain to check if the data is available."""

        return self._app.retrieve(self._transaction['key']) == \
               self._transaction['value']


class Storage:
    def __init__(self, bootstrap, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._address = '127.0.0.1:5002'
        server = Thread(target=app.run())

        """
        self._blockchain = Blockchain(bootstrap, difficulty)
        if miner:
            new_block = self._blockchain.mine()
        """


    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        api_url = 'http://' + self._address + '/put'

        data = {'origin': self._address,
                'key':key,
                'value':value}

        r = requests.get(api_url, data)
        if r.status_code != 200:
            print("[ERROR] No connection for retrieve value")
            return -1

        callback = Callback(data, self)
        if block:
            callback.wait()
        return callback


    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        return self.retrieve_all(key, True)


    def retrieve_all(self, key, last=False):
        """
        Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        api_url = 'http://'+self._address+'/chain'
        r = requests.get(api_url)
        if r.status_code != 200:
            print("[ERROR] No connection for retrieve blockchain")
            return -1
        chain = r.json()["chain"]

        results = []
        for block in reversed(chain):
            for transaction in reversed(block['_transactions']):
                if transaction['key'] == key:
                    if last: #Last value stored = retrieve
                        return transaction['value']
                    results.append(transaction['value'])
        return results
