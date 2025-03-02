// Generate Wallet
document.getElementById('generate_wallet').addEventListener('click', () => {
    fetch('/wallet/new', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const walletDetails = document.getElementById('wallet_details');
            const publicKey = truncateKey(data.public_key);
            const privateKey = truncateKey(data.private_key);

            walletDetails.innerHTML = `
                <h3>Wallet Details</h3>
                <p><strong>Public Key:</strong> ${publicKey}</p>
                <p><strong>Private Key:</strong> ${privateKey}</p>
                <p><strong>Full Public Key:</strong> <span class="full-key">${data.public_key}</span></p>
                <p><strong>Full Private Key:</strong> <span class="full-key">${data.private_key}</span></p>
            `;
        })
        .catch(error => console.error('Error generating wallet:', error));
});

// Helper function to truncate keys
function truncateKey(key, maxLength = 20) {
    if (key.length > maxLength) {
        return `${key.substring(0, maxLength)}...`;
    }
    return key;
}