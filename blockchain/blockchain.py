import binascii
import hashlib
import json
from collections import OrderedDict
from time import time
from uuid import uuid4
from urllib.parse import urlparse

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# Constants
MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 2


class Blockchain:
    """Represents the blockchain and its operations."""

    def __init__(self):
        """Initialize the blockchain with an empty list of transactions and an empty chain."""
        self.transactions = []
        self.chain = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-', '')
        self.create_block(0, '00')  # Create the genesis block

    def register_node(self, node_url):
        """
        Add a new node to the list of nodes.

        :param node_url: URL of the node to be added.
        :raises ValueError: If the URL is invalid.
        """
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Verify the signature of a transaction.

        :param sender_address: Public key of the sender.
        :param signature: Signature of the transaction.
        :param transaction: Transaction data.
        :return: True if the signature is valid, False otherwise.
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        transaction_hash = SHA256.new(str(transaction).encode('utf8'))
        return verifier.verify(transaction_hash, binascii.unhexlify(signature))

    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a transaction to the list of transactions.

        :param sender_address: Address of the sender.
        :param recipient_address: Address of the recipient.
        :param value: Amount to be transferred.
        :param signature: Signature of the transaction.
        :return: Index of the block that will contain this transaction.
        """
        transaction = OrderedDict({
            'sender_address': sender_address,
            'recipient_address': recipient_address,
            'value': value
        })

        if sender_address == MINING_SENDER:
            # Mining reward transaction
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            # Regular transaction
            if self.verify_transaction_signature(sender_address, signature, transaction):
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False

    def create_block(self, nonce, previous_hash):
        """
        Create a new block in the blockchain.

        :param nonce: The nonce value for the block.
        :param previous_hash: Hash of the previous block.
        :return: The newly created block.
        """
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        # Reset the list of transactions
        self.transactions = []

        self.chain.append(block)
        return block

    def hash(self, block):
        """
        Create a SHA-256 hash of a block.

        :param block: Block to be hashed.
        :return: Hash of the block.
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self):
        """
        Perform proof-of-work to find a valid nonce.

        :return: The valid nonce.
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while not self.valid_proof(self.transactions, last_hash, nonce):
            nonce += 1

        return nonce

    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions.

        :param transactions: List of transactions.
        :param last_hash: Hash of the last block.
        :param nonce: The nonce value.
        :param difficulty: Mining difficulty.
        :return: True if the hash is valid, False otherwise.
        """
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def valid_chain(self, chain):
        """
        Check if a blockchain is valid.

        :param chain: The blockchain to be validated.
        :return: True if the chain is valid, False otherwise.
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            transactions = block['transactions'][:-1]
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between nodes by replacing the chain with the longest valid one.

        :return: True if the chain was replaced, False otherwise.
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


# Flask App
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


@app.route('/configure')
def configure():
    """Render the configuration page."""
    return render_template('configure.html')


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Add a new transaction to the blockchain."""
    values = request.get_json()
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400

    transaction_result = blockchain.submit_transaction(
        values['sender_address'],
        values['recipient_address'],
        values['amount'],
        values['signature']
    )

    if not transaction_result:
        return jsonify({'message': 'Invalid Transaction!'}), 406
    else:
        return jsonify({'message': f'Transaction will be added to Block {transaction_result}'}), 201


@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    """Get the list of unmined transactions."""
    response = {
        'transactions': blockchain.transactions
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    """Get the full blockchain."""
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    """Mine a new block."""
    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    blockchain.submit_transaction(
        sender_address=MINING_SENDER,
        recipient_address=blockchain.node_id,
        value=MINING_REWARD,
        signature=""
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': "New Block Forged",
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Register new nodes with the blockchain."""
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return jsonify({'message': 'Error: Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """Resolve conflicts between nodes."""
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    """Get the list of registered nodes."""
    response = {
        'nodes': list(blockchain.nodes)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)