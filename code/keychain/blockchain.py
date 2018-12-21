"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import requests
from block import Block
from transaction import Transaction
from flask import jsonify


class Blockchain:
    def __init__(self, bootstrap, difficulty, myport):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        self._address = '127.0.0.1' + ":" + myport

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
        block._transactions = self._transactions
        self._transactions = [] #Reset the actual transactions

        self._blocks.append(block)
        return block

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
        for block_dict in chain_data:
            block = Block()
            block.timestamp = block_dict['timestamp']
            block.blockNo = block_dict['blockNo']
            block.prev_hash = block_dict['prev_hash']
            block.proof = block_dict['proof']
            _t = []
            for t in block_dict['_transactions']:
                _t.append(Transaction(t['origin'], t['key'], t['value']))
            block._transactions = _t

            builded_chain.append(block)
        return builded_chain

    def valid_block(self, block):
        prev_block = self._blocks[-1]
        return  prev_block.get_hash() == block.get_prevhash() and \
                prev_block.get_blockNo() + 1 == block.get_blockNo() and \
                self._valid_proof(prev_block.get_proof(),
                                   prev_block.get_hash(),
                                   block.get_proof()) and \
               prev_block.timestamp <= block.timestamp

        # BOOTSTRAP AND CONFLICTS WITH THE CHAIN -----------------------------------

    def vote_chain(self):
        chains = {}
        chains_data = {}
        for peer in self._peers:
            api_url = 'http://' + peer + '/chain'
            r = requests.get(api_url)
            if r.status_code != 200:
                print("[ERROR] No connection for blockchain")
                return -1
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
        print("Best is:", best)
        print("Best addresses:", chains[best])
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
        self._blocks = builded
        if self.is_valid():
            return True
        return False
        # --------------------

    #TODO----------------------------------------------
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
            petition = 'http://' + peer + '/register'  # TODO
            try:
                r = requests.get(petition, {'address': self._address})
            except:
                print("[ERROR] Request in peer ", peer)
                self._peers.remove(peer)
            if r.status_code != 200:
                print("[ERROR] No connection with peer on: " + peer)
                self._peers.remove(peer)
                # TODO: SEND OTHER PEERS THAT THIS PEER IS NOT RESPONDING?

            # testing purpose:
            r = requests.get('http://' + peer + '/peers')
            print(r.json())
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
                             transaction.get_transaction())
            #Ack of the transaction?
            if r.status_code == 200 and r.json()['transaction'] == \
                    transaction.get_hash():
                acks.append(peer)
        if len(self._peers) == len(acks):
            return True
        return False





    def mine(self):
        """Implements the mining procedure."""

        last_block = self._blocks[-1]
        proof = self.proof_of_work(last_block)

        new_block = self.add_block(proof)
        print("[MINING] BLOCK " + str(new_block.blockNo) + " MINED")

        for peer in self._peers:
            # POST method on the peer address
            data = {
                'message': "Block mined",
                'blockNo': new_block.get_blockNo(),
                'transactions': new_block.get_transactions(),
                'proof': new_block.get_proof(),
                'prev_hash': new_block.get_prevhash(),
            }
            r = requests.post('http://' + peer + '/newblock',
                              data=data)
        return new_block