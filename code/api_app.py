import requests
from flask import Flask, request, jsonify
from block import Block
from transaction import Transaction
from blockchain import Blockchain


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")

    arguments, _ = parser.parse_known_args()
    return arguments

import socket
address = socket.gethostbyname(socket.gethostname())

#CONFIGURATION
app = Flask(__name__)
blockchain = Blockchain(parse_arguments().bootstrap,
                        parse_arguments().difficulty,
                        parse_arguments().port)


#RECEIVE OBJECTS
@app.route('/transaction')
def receive_transaction():
    """
    Receive a transaction from other peers
    :return:
    """
    t = request.args
    o = t['origin']
    k = t['key']
    v = t['value']
    tran = Transaction(o, k, v)
    h = blockchain.add_transaction(tran)
    return jsonify({'transaction': h})

@app.route("/put")
def put():
    """
    Register a new value with key in the block
    :return:
    """
    t = request.args
    o = t['origin']
    k =  t['key']
    v =  t['value']
    tran = Transaction(o, k, v)
    blockchain.add_transaction2(tran)
    return jsonify({'transaction': tran.get_hash()})


@app.route('/newblock')
def receive_block():
    """
    Receive a new mined block, validate it and if valid add to chain
    :return:
    """
    data = request.get_json()
    new_block = Block()
    #TODO

    response = {'message': f'Block received'}
    return jsonify(response)


#FULL CHAIN
@app.route('/chain')
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

    return jsonify({'chain': blocks})


#PEERS
@app.route("/register")
def register_peer():
    """
    Add to the list of peers the peer that called
    :return:
    """
    addr = request.args['address']
    blockchain.add_peer(addr)
    return jsonify({'message': 'OK'})

@app.route("/peers")
def send_peers():
    """
    Send local list of peers to the caller
    :return: list of peers
    """
    return jsonify({'peers': blockchain._peers})

@app.route("/resolve")
def resolve_conflict():
    """
    Receive a petition that inform his chain is not the most common in the
    network
    :return:
    """
    chain_data = request.args['chain']
    blockchain.replace_chain(chain_data)
    return jsonify({'message': 'OK'})

#New transaction

#MINER
@app.route("/mine")
def mine():
    """
    The peer will be mining
    :return:
    """
    blockchain.mine()
    return jsonify({'mining': True})

#bcast / check nodes / block new

#If app not in the end = 404
#Maybe launched with python call systems from Store
app.run(debug=True, port=parse_arguments().port)