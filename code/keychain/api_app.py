import requests
from flask import Flask, request, jsonify
from block import Block
from transaction import Transaction
from blockchain import Blockchain


def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    arguments, _ = parser.parse_known_args()
    return arguments

import socket
address = socket.gethostbyname(socket.gethostname())
port = str(parse_arguments().port)

t ='127.0.0.1'+ ":" + port
b = '127.0.0.1' + ":" + str(5001)
diff = 4

app = Flask(__name__)
blockchain = Blockchain(b, diff, port)

#RECEIVE OBJECTS
@app.route('/transaction', methods=['POST'])
def receive_transaction():
    """
    Receive a transaction from other peers
    :return:
    """
    data = request.get_json()
    transaction = Transaction(data['origin'], data['key'], data['value'])
    blockchain._transactions.append(transaction)
    response = {'message': 'Transaction received'}
    return jsonify(response)

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
    return jsonify(response)


#FULL CHAIN
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

    return jsonify({'chain': blocks})


#PEERS
@app.route("/register", methods=['GET'])
def register_peer():
    """
    Add to the list of peers the peer that called
    :return:
    """
    addr = request.args['address']
    blockchain.add_peer(addr)
    return jsonify({'message': 'OK'})

@app.route("/peers", methods=['GET'])
def send_peers():
    """
    Send local list of peers to the caller
    :return: list of peers
    """
    return jsonify({'peers': blockchain._peers})


#New transaction
@app.route("/put", methods=['POST'])
def put():
    """
    Register a new value with key in the block
    :return:
    """
    o = request.get_json()['origin']
    k =  request.get_json()['key']
    v =  request.get_json()['value']
    blockchain.add_transaction(Transaction(o, k, v))
    return jsonify({'transaction': 0})

#MINER
@app.route("/mine", methods=['GET'])
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