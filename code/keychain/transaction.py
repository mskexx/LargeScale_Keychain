import hashlib

class Transaction:
    def __init__(self, origin, key, value):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self.key = key
        self.value = value
        self.origin = origin
        self.timestamp = datetime.datetime.now()

    def get_transaction(self):
        return {"key"   : self.key,
                "value": self.value,
                "origin": self.origin}

    def get_hash(self):
        h = hashlib.sha256()
        h.update(
            str(self.key).encode('utf-8') +
            str(self.value).encode('utf-8') +
            str(self.origin).encode('utf-8')+
            str(self.timestamp).encode('utf-8'))
        return h.hexdigest()

