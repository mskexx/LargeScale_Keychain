"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import requests
from block import Block
from transaction import Transaction
import json
from datetime import datetime
import time
import copy
from threading import Thread
class TestEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Transaction):
            return o.raw_transaction()
        elif isinstance(o, datetime):
            return o.isoformat()
        print(o)
        return json.JSONEncoder.default(self, o)

class Blockchain:
    transactions = []
    def __init__(self, bootstrap, difficulty, myport, mine=False):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        self._address = '127.0.0.1' + ":" + str(myport)
        # Initialize the properties.

        self._blocks = []
        self._peers = []
        self._difficulty = difficulty

        self._transactions = []
        # Initialize the chain with the Genesis block.
        self._add_genesis_block()
        # Bootstrap the chain with the specified bootstrap address.

        if bootstrap != self._address:
            if not self._bootstrap(bootstrap):
                print("[ERROR] Bootstrap not completed")
        if mine:
            miner = Thread(target=self.mine, daemon=True)
            miner.start()


    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        self._blocks.append(Block())

    def difficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        if (self._blocks[-1].get_blockNo()+1) != len(self._blocks):
            return False

        prev_block = None
        for index, block in enumerate(self._blocks):
            if prev_block:
                if prev_block.get_hash() != block.get_prevhash():
                    return False

                elif prev_block.get_blockNo() + 1 != block.get_blockNo():
                    return False

                elif not self._valid_proof(prev_block.get_proof(),
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
        if self._valid_proof(prev_block.get_proof(), prev_block.get_hash(),
                             proof):

            block._transactions = copy.deepcopy(self._transactions)
            self._blocks.append(block)
            return block
        return None

    def proof_of_work(self, last_block):
        p_proof = last_block.proof
        p_hash = last_block.get_hash()
        proof = 0
        while not self._valid_proof(p_proof, p_hash, proof):
            proof +=1
        return proof

    def _valid_proof(self, prev_proof, prev_hash, proof):
        difficulty = self.difficulty()
        h = hashlib.sha256()
        h.update(
            str(prev_proof).encode('utf-8') +
            str(prev_hash).encode('utf-8') +
            str(proof).encode('utf-8'))
        try_hash = h.hexdigest()
        return try_hash[:difficulty] == '0'*difficulty

    def add_peer(self, address):
        """
        Adds a peer to the blockchain peers
        """
        if address not in self._peers:
            self._peers.append(address)

    def chain_from_json(self, chain_data):
        builded_chain = []
        for bd in chain_data:
            try:
                block_dict = json.loads(str(bd))
            except:
                block_dict = bd
            block = Block()
            block.timestamp = block_dict['timestamp']
            block.blockNo = block_dict['blockNo']
            block.prev_hash = block_dict['prev_hash']
            block.proof = block_dict['proof']

            ts = block_dict['_transactions']
            _t = [Transaction(t['origin'], t['key'], t['value'],
                                      t['timestamp']) for t in ts]
            block._transactions = _t
            builded_chain.append(block)

        return builded_chain

    def block_from_json(self, block_data):
        for l in block_data:
            block_data = json.loads(l)
        block = Block()  # New block
        block.prev_hash = block_data['prev_hash']
        block.blockNo = block_data['blockNo']
        block.proof = block_data['proof']
        block.timestamp = block_data['timestamp']

        conf_transactions = []
        for t in block_data['_transactions']:
            t1 = Transaction(t['origin'], t['key'], t['value'], t['timestamp'])

            if t1 in self._transactions:
                conf_transactions.append(t1)
            else:
                print("[ERROR] Possible not syncro with other transactions")
                return None

        block._transactions = conf_transactions
        if self.valid_block(block):
            return block
        return None

    def valid_block(self, block):
        prev_block = self._blocks[-1]
        '''
        print("--------------------------------------")
        print("Prev hash", prev_block.get_hash())
        print("Block prev hash", block.get_prevhash())
        print("--------------------------------------")
        print("Block no >", prev_block.get_blockNo(), block.get_blockNo())
        print("--------------------------------------")
        '''
        p1 = prev_block.get_hash() == block.get_prevhash()
        p2 = prev_block.get_blockNo() + 1 == block.get_blockNo()
        p3 =  self._valid_proof(prev_block.get_proof(), prev_block.get_hash(),
                                   block.get_proof())

        return p1 and p2 and p3

        # BOOTSTRAP AND CONFLICTS WITH THE CHAIN -----------------------------------

    def vote_chain(self):
        chains = {}
        chains_data = {}
        for peer in self._peers:
            api_url = 'http://' + peer + '/chain'
            r = requests.get(api_url)
            if r.status_code != 200:
                print("[ERROR] No connection for blockchain")
                return [], 0
            chain = r.json()["chain"]
            builded = self.chain_from_json(chain)
            hashes = [block.get_hash() for block in builded]
            chain_hash = ''.join(hashes)

            if chain_hash not in chains:
                chains[chain_hash] = []
                chains_data[chain_hash] = chain
            chains[chain_hash].append(peer)

        best = max(chains, key=lambda x: chains[x])
        addresses = chains[best]
        #print("Best is:", best)
        #print("Best addresses:", chains[best])
        return addresses, chains_data[best]

    def ask_chain(self, peers):
        for peer in peers:
            api_url = 'http://' + peer + '/chain'
            r = requests.get(api_url)
            if r.status_code != 200:
                print("[ERROR] No connection for blockchain")
                return -1
            return r.json()["chain"]
        return None

    def replace_chain(self, chain_data=None):
        builded = self.chain_from_json(chain_data)
        save = copy.deepcopy(self._blocks)
        self._blocks = builded
        if self.is_valid():
            return True
        self._blocks = save
        return False
        # --------------------

    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""
        # Ask for peers to address ----------------------------------------------
        r = requests.get('http://' + address + '/peers')
        if r.status_code != 200:
            print("[BOOTSTRAP] Bootstrap address not available")
            return -1

        self.add_peer(address)
        l_peers = r.json()['peers']
        if self._address in l_peers:
            l_peers.remove(self._address)

        for peer in l_peers:
            self.add_peer(peer)

        for peer in self._peers:  # Register new node in the other lists
            petition = 'http://' + peer + '/register'
            try:
                r = requests.get(petition, {'address': self._address})
            except:
                print("[ERROR] Request in peer ", peer)
                self._peers.remove(peer)
            if r.status_code != 200:
                print("[ERROR] No connection with peer on: " + peer)
                self._peers.remove(peer)

        # -----------------------------------------------------------------------
        # bcast to get the blockchain
        winners, chain_data = self.vote_chain()
        losers = list(set(self._peers) - set(winners))
        for peer in losers:
            petition = 'http://' + peer + '/resolve'
            r = requests.get(petition, {'chain': chain_data})
            if r.status_code != 200:
                print("[ERROR] No connection with peer on: " + peer)

        if self.replace_chain(chain_data):
            return True
        return False

    def add_transaction(self, transaction):
        print("[TRANSACTION] Transaction added to pool")
        self._transactions.append(transaction)
        Blockchain.transactions.append(transaction)
        return transaction.get_hash()

    def add_transaction2(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        acks = []
        self._transactions.append(transaction)
        #Now broadcast?
        print("Starting broadcast of transaction")
        for peer in self._peers:
            #send transaction to all
            r = requests.get('http://'+peer+'/transaction',
                             transaction.raw_transaction())
            #Ack of the transaction?
            if r.status_code == 200 and r.json()['transaction'] == \
                    transaction.get_hash():
                acks.append(peer)
        if len(self._peers) == len(acks):
            return True
        return False

    def to_json(self):
        chain = []
        for block in self._blocks:
            chain.append(self.block_to_json(block))
        return chain

    def block_to_json(self, block):
        return json.dumps(block.__dict__, sort_keys=True,
                   cls=TestEncoder)

    def mine(self):
        """Implements the mining procedure."""
        import timeit
        print("START MINING")
        while True:
            if len(self._transactions) < 1:
                time.sleep(2)
            else:
                last_block = self._blocks[-1]
                proof = self.proof_of_work(last_block)
                new_block = self.add_block(proof)
                if new_block:
                    for t in new_block.get_transactions():
                        self._transactions.remove(t)

                    #print("[MINING] BLOCK " + str(new_block.blockNo) +
                    #     "MINED: "+new_block.get_hash())

                    data = json.dumps(new_block.__dict__, sort_keys=True,
                    cls=TestEncoder)

                    for peer in self._peers:
                        r = requests.get('http://' + peer + '/newblock', data)
                        if r.status_code != 200:
                            print("[ERROR] Sending mined block to peer on: ", peer)