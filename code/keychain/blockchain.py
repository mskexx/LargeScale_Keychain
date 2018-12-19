"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""
import hashlib
import requests
from flask import Flask, request, jsonify

from keychain import Block
from keychain import Transaction

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
        addres, download the peerlist, and start the bootstrapping procedure.
        """
        self._addr = '127.0.0.1:5000'
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
        self._blocks.append(Block())


    def _bootstrap(self, address):
        """Implements the bootstrapping procedure."""
        peer = Peer(address)
        #Ask for peers to address
        #Then start bootstrapping for example.. the peer with longest chain
        r = requests.get('http://'+peer.get_address()+'/peers')
        self._peers = r['peers']
        self.resolve_conflicts()


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

    def is_valid2(self, chain):
        prev_block = None
        for index, block in enumerate(chain._blocks):
            if prev_block:
                if prev_block.get_hash() != block.get_prevhash():
                    return False

                elif prev_block.get_blockNo() + 1 != block.get_blockNo():
                    return False

                elif not chain.valid_proof(prev_block.get_proof(),
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
        self._peers.append(address)

    def resolve_conflicts(self):
        """
        Resolve the conflict in the peer replacing the chain with the longest
        one existing in the network
        """
        longest_chain = None
        max_length = len(self._blocks)

        for peer in self._peers:
            response = requests.get(f'http://{peer}/chain')

            if response.status_code == 200:
                chain = response.json()['chain']

                if len(chain) > max_length and self.is_valid2(chain):
                    max_length = len(chain)
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    #--------------------------------------------------------------------------
app = Flask(__name__)
blockchain = Blockchain('127.0.0.1', 4)
app.run(debug=True, port=5000)


@app.route('/transaction', methods=['POST'])
def receive_transaction():
    """
    Receive a transaction from other peers
    :return:
    """
    data = request.get_json()
    transaction = Transaction(data['origin'], data['key'], data['value'])
    blockchain._transactions.append(transaction)
    response = {'message': f'Transaction received'}
    return jsonify(response), 201

@app.route('/newblock', methods=['POST'])
def receive_block():
    """
    Receive a new mined block, validate it and if valid add to chain
    :return:
    """
    data = request.get_json()
    new_block = Block()
    #TODO

    response = {'message': f'Block received'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def chain():
    """
    Obtains the local chain and put it into json forman
    :return: Local chain to the peer
    """
    blocks = []
    for block in blockchain._blocks:
        transactions = [vars(t) for t in block._transactions]
        b = vars(block)
        b['_transactions'] = transactions
        blocks.append(b)

    #TODO list json - dumps?
    return jsonify({'chain': blocks}), 200

#Related with register / ask peers
@app.route("/register", methods=['POST'])
def register_peer():
    """
    Registers the peer that called the method
    :return:
    """
    data = request.get_json()
    blockchain.add_peer(data['address'])
    return 0 #TODO

@app.route("/mine", methods=['GET'])
def mine():
    """
    The peer will be mining
    :return:
    """
    blockchain.mine()