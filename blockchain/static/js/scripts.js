// Fetch and display unmined transactions
function fetchTransactions() {
    fetch('/transactions/get')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('unmined_transactions_table');
            table.innerHTML = `
                <tr>
                    <th>#</th>
                    <th>Recipient Address</th>
                    <th>Sender Address</th>
                    <th>Value</th>
                </tr>
            `;
            if (data.transactions.length === 0) {
                table.innerHTML += `
                    <tr>
                        <td colspan="4" class="placeholder">No data available in table</td>
                    </tr>
                `;
            } else {
                data.transactions.forEach((transaction, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${transaction.recipient_address}</td>
                        <td>${transaction.sender_address}</td>
                        <td>${transaction.value}</td>
                    `;
                    table.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error fetching transactions:', error));
}

// Mine a new block
document.getElementById('mine_button').addEventListener('click', () => {
    fetch('/mine', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchTransactions(); // Refresh transactions after mining
        })
        .catch(error => console.error('Error mining block:', error));
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchTransactions();
});