"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import datetime

class Block:
    def __init__(self):
        """Describe the properties of a block."""
        self._transactions = []
        self.blockNo = 0
        self.proof = None
        self.prev_hash = 0x0
        self.timestamp = datetime.datetime.now()

    def get_proof(self):
        """Return the proof of the current block."""
        return self.proof

    def get_transactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transactions

    def get_hash(self):
        h = hashlib.sha256()
        h.update(
            str(self.proof).encode('utf-8') +
            str(self._transactions).encode('utf-8') +
            str(self.prev_hash).encode('utf-8') +
            str(self.timestamp).encode('utf-8') +
            str(self.blockNo).encode('utf-8'))

        return h.hexdigest()

    def get_prevhash(self):
        """Return the hash of the previous block."""
        return self.prev_hash

    def get_blockNo(self):
        """ Return the block number"""
        return self.blockNo

    def set_genesis(self, transactions):
        self.prev_hash = 0x0
        self.nonce = 0
        self._transactions = transactions
        self.blockNo = 0
        self.proof = 0
        self.hash = self.get_hash()

class Transaction:
    def __init__(self, origin, key, value):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self.key = key #Key
        self.value = value
        self.origin = origin

        #raise NotImplementedError
    def get_transaction(self):
        return {"key"   : self.key,
                "value": self.value,
                "origin": self.origin}


class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address


class Blockchain:
    def __init__(self, bootstrap, difficulty):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        addres, download the peerlist, and start the bootstrapping procedure.
        """

        # Initialize the properties.
        self._blocks = []
        self._peers = []
        self._difficulty = difficulty

        self._transactions = []
        # Initialize the chain with the Genesis block.
        self._add_genesis_block()

        # Bootstrap the chain with the specified bootstrap address.
        self._bootstrap(bootstrap)


    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        block = Block()
        block.set_genesis(self._transactions)
        self._transactions = [] #Reset transactions

        self._blocks.append(block)


    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""
        peer = Peer(address)
        return 0 #TODO

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self._transactions.append(transaction)
        #Now broadcast?
        return 0
    def mine(self):
        """Implements the mining procedure."""
        last_block = self._blocks[-1]
        proof = self.proof_of_work(last_block)

        node_test = 9999999999
        reward_transaction = Transaction(origin="0",
                                         key=node_test,
                                         value=1)
        self.add_transaction(reward_transaction)
        new_block = self.add_block(proof)

        print(">> BLOCK "+str(new_block.blockNo) + " MINED")
        self.is_valid()
        return 0

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        prev_block = None
        for index, block in enumerate(self._blocks):
            if  prev_block:
                if prev_block.get_hash() != block.get_prevhash():
                    return False

                elif prev_block.get_blockNo() + 1 != block.get_blockNo():
                    return False

                elif not self.valid_proof(prev_block.get_proof(),
                                      prev_block.get_hash(),
                                      block.get_proof()):
                    return False

                elif prev_block.timestamp >= block.timestamp:
                    return False

            prev_block = block
        return True

    def add_block(self, proof):
        prev_block = self._blocks[-1]

        block = Block()  # New block
        block.prev_hash = prev_block.get_hash()
        block.blockNo = prev_block.blockNo + 1
        block.proof = proof

        #Check current block is correct ---------------
        if len(self._blocks) == prev_block.blockNo:
            print("Chain number is correct")
        #----------------------------------------------

        block._transactions = self._transactions
        self._transactions = [] #Reset the actual transactions

        self._blocks.append(block)
        return block

    def proof_of_work(self, last_block):
        p_proof = last_block.proof
        p_hash = last_block.get_hash()
        proof = 0
        while not self.valid_proof(p_proof, p_hash, proof):
            proof +=1
        return proof

    def valid_proof(self, prev_proof, prev_hash, proof):
        difficulty = self.difficulty()
        h = hashlib.sha256()
        h.update(
            str(prev_proof).encode('utf-8') +
            str(prev_hash).encode('utf-8') +
            str(proof).encode('utf-8'))
        try_hash = h.hexdigest()
        return try_hash[:difficulty] == '0'*difficulty


