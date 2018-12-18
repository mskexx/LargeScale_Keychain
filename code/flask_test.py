from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'test'

@app.route('/blockchain')
def blocks():
    blockchain = [1,2,3,4]
    return blockchain

@app.route('/peers')
def peers():
    peer_list = ['0.0.0.1', '0.0.0.2']
    return peer_list


if __name__ == '__main__':
    app.run(debug=True)