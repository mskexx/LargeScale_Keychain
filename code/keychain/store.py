"""
KeyChain key-value store (stub).

NB: Feel free to extend or modify.
"""

from keychain import Blockchain
from keychain import Transaction


class Callback:
    def __init__(self, transaction, chain):
        self._transaction = transaction
        self._chain = chain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""
        return 0 #TODO

    def completed(self):
        """Polls the blockchain to check if the data is available."""
        return 0 #TODO


class Storage:
    def __init__(self, bootstrap, miner, difficulty):
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        self._blockchain = Blockchain(bootstrap, difficulty)

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.
        """
        #TODO
        transaction = Transaction("0", key, value)
        self._blockchain.add_transaction(transaction)
        callback = Callback(transaction, self._blockchain)
        if block:
            callback.wait()

        return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        for block in reversed(self._blockchain._blocks):
            for transaction in block.get_transactions():
                info = transaction.get_transaction()
                if info['key'] == key:
                    return info['value']
        return "ERROR: No value for " + str(key)

    def retrieve_all(self, key):
        """
        Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        results = []
        for block in reversed(self._blockchain._blocks):
            for transaction in block.get_transactions():
                info = transaction.get_transaction()
                if info['key'] == key:
                    print("Found in block ", block.blockNo, info["value"])
                    results.append(info['value'])
        return results