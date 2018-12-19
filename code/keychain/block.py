import datetime
import hashlib

class Block:
    def __init__(self):
        """Describe the properties of a block."""
        self._transactions = []
        self.blockNo = 0
        self.proof = None
        self.prev_hash = 0x0
        self.timestamp = datetime.datetime.now()

    def get_block(self): #Or maybe __dict__  better
        return {'blockNo': self.blockNo,
                'proof': self.proof,
                'prev_hash': self.prev_hash,
                'timestamp': self.timestamp}

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