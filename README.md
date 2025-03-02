# Blockchain Project

A simple blockchain implementation with a Flask-based backend and a frontend for interacting with the blockchain. This project demonstrates the core concepts of blockchain technology, including transactions, mining, and consensus.

---

## Features

- **Create Wallets**: Generate public and private keys for users.
- **Submit Transactions**: Send transactions between wallets.
- **Mine Blocks**: Add new blocks to the blockchain by solving proof-of-work.
- **Consensus Mechanism**: Resolve conflicts between nodes to maintain a consistent blockchain.
- **View Blockchain**: Explore the entire blockchain and its transactions.

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

---
API Endpoints
Blockchain Backend (blockchain.py)

    GET /: Render the index page.

    GET /configure: Render the node configuration page.

    POST /transactions/new: Submit a new transaction.

    GET /transactions/get: Get the list of unmined transactions.

    GET /chain: Get the full blockchain.

    GET /mine: Mine a new block.

    POST /nodes/register: Register new nodes.

    GET /nodes/resolve: Resolve conflicts between nodes.

    GET /nodes/get: Get the list of registered nodes.
---

Blockchain Client (client.py)

    GET /: Render the wallet generator page.

    GET /make/transaction: Render the transaction creation page.

    GET /view/transactions: Render the transaction viewing page.

    GET /wallet/new: Generate a new wallet (public and private keys).

    POST /generate/transaction: Generate and sign a new transaction.

---
  Usage

    Generate a Wallet:

        Visit http://127.0.0.1:8080 to generate a new wallet.

        Save your public and private keys securely.

    Submit a Transaction:

        Use the generated keys to send transactions.

        Visit http://127.0.0.1:8080/make/transaction to create a transaction.

    Mine a Block:

        Visit http://127.0.0.1:5000/mine to mine a new block and add transactions to the blockchain.

    View the Blockchain:

        Visit http://127.0.0.1:5000/chain to view the entire blockchain.

    Add Nodes:

        Use the /nodes/register endpoint to add new nodes to the network.

    Resolve Conflicts:

        Use the /nodes/resolve endpoint to ensure your blockchain is up-to-date.
