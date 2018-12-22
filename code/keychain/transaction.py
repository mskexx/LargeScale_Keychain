import hashlib
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

class Transaction:
    def __init__(self, origin, key, value, t=False):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self.key = key
        self.value = value
        self.origin = origin
        if not t:
            self.timestamp = datetime.now().isoformat()
        else:
            self.timestamp = t

    def raw_transaction(self):
        return{"key"   : self.key,
                "value": self.value,
                "origin": self.origin,
                "timestamp": self.timestamp}

    def get_hash(self):
        h = hashlib.sha256()
        h.update(
            str(self.key).encode('utf-8') +
            str(self.value).encode('utf-8') +
            str(self.origin).encode('utf-8')+
            str(self.timestamp).encode('utf-8'))
        return h.hexdigest()

    def __eq__(self, other):
        return self.get_hash() == other.get_hash()
