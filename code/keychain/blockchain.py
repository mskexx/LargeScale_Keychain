"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import requests
from block import Block
from transaction import Transaction

class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address

    def get_address(self):
        return str(self._address)

class Blockchain:
    def __init__(self, bootstrap, difficulty):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        self._address = '127.0.0.1:5001' #TODO
        # Initialize the properties.

        self._blocks = []
        self._peers = []
        self._difficulty = difficulty

        self._transactions = []
        # Initialize the chain with the Genesis block.
        self._add_genesis_block()
        # Bootstrap the chain with the specified bootstrap address.
        if bootstrap != self._address:
            self._bootstrap(bootstrap)


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
        self._peers.append(Peer(address))

    def build_chain(self, chain_data):
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

    #TODO----------------------------------------------

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self._transactions.append(transaction)
        #Now broadcast?
        print("Starting broadcast of transaction")
        for peer in self._peers:
            #send transaction to all
            r = requests.post('http://'+peer.get_address()+'/transaction',
                                     data=transaction.get_transaction())
            #Ack of the transaction?

        return 0

    def mine(self):
        """Implements the mining procedure."""

        last_block = self._blocks[-1]
        proof = self.proof_of_work(last_block)

        new_block = self.add_block(proof)
        print(">> BLOCK " + str(new_block.blockNo) + " MINED")

        for peer in self._peers:
            # POST method on the peer address
            data = {
                'message': "Block mined",
                'blockNo': new_block.get_blockNo(),
                'transactions': new_block.get_transactions(),
                'proof': new_block.get_proof(),
                'prev_hash': new_block.get_prevhash(),
            }
            r = requests.post('http://' + peer.get_address() + '/newblock',
                              data=data)
        return new_block

    def resolve_conflicts(self, peers):
        """
        Resolve the conflict in the peer replacing the chain with the longest
        one existing in the network

        #TODO 1: New node in network
            - Get peers
        #TODO 2: ---

        #TODO: Check each chain -> bcast

        """
        longest_chain = None
        max_length = len(self._blocks)
        chain_peer = None
        for peer in peers:
            response = requests.get(f'http://{peer}/chain')

            if response.status_code == 200:
                chain = response.json()['chain']

                if len(chain) > max_length:
                    max_length = len(chain)
                    longest_chain = chain
                    chain_peer = peer

        if longest_chain:
            chain = self.build_chain(longest_chain)
            self.chain = chain
            if self.is_valid():
                return True, chain_peer
            return False, chain_peer
        return False, chain_peer


    def vote_chain(self):
        chains = {}
        for peer in self._peers:
            api_url = 'http://' + peer.get_address() + '/chain'
            r = requests.get(api_url)
            if r.status_code != 200:
                print("[ERROR] No connection for blockchain")
                return -1
            chain = r.json()["chain"]

            #Maybe chain to hash-->
            if chain not in chains:
                chains[chain] = {'votes': 0, 'peers':[]}

            chains[chain]['votes'] += 1
            chains[chain]['peers'].append(peer.get_address())

        best = max(chains, key=lambda x: chains[x]['votes'])
        addresses = chains[best]['peers']
        return best, addresses




    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""

        #Ask for peers to address ----------------------------------------------
        r = requests.get('http://'+address+'/peers')
        if r.status_code != 200:
            print("[BOOTSTRAP] Bootstrap address not available")
            return -1

        self.add_peer(address)
        for peer in r['peers']:
            self.add_peer(peer)

        for peer in self._peers: #Register new node in the other lists
            petition = 'http://'+peer.get_address()+'/register'
            requests.post(petition, data={'address':self._address})
        #-----------------------------------------------------------------------
        #bcast to get the blockchain
        tmp_peers = self._peers
        correct, peer = self.resolve_conflicts(tmp_peers) #Get longest chain
        while not correct and tmp_peers:
            print("[BOOTSTRAP] Bootstraped chain is not valid, trying again")
            correct, peer = self.resolve_conflicts(tmp_peers)
            tmp_peers = tmp_peers.remove(peer)

        if not correct and not peer: #No chain or self chain is the best
            print("[BOOTSTRAP] No chain to bootstrap")
        return
