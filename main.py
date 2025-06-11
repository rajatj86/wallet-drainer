from web3 import Web3
import os
from dotenv import load_dotenv
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Chain configuration
CHAINS = {
    'bsc': {
        'rpc_urls': [
            'https://bsc-dataseed.binance.org/',
            'https://bsc-dataseed1.defibit.io/',
            'https://bsc-dataseed1.ninicoin.io/',
            'https://bsc.publicnode.com'
        ],
        'chain_id': 56,
        'gas_price_gwei': 7,
        'block_time_seconds': 3
    },
    'ethereum': {
        'rpc_urls': [
            'https://rpc.ankr.com/eth',
            'https://1rpc.io/eth',
            'https://api.zan.top/eth-mainnet',
            'https://eth.llamarpc.com',        
        ],
        'chain_id': 1,
        'gas_price_gwei': 20,
        'block_time_seconds': 12
    },
    'polygon': {
        'rpc_urls': [
            'https://rpc.ankr.com/polygon',
            'https://1rpc.io/matic',
            'https://polygon-bor-rpc.publicnode.com',
        ],
        'chain_id': 137,
        'gas_price_gwei': 50,
        'block_time_seconds': 3
    },
    'Linea': {
        'rpc_urls': [
            'https://linea.drpc.org',
            'https://rpc.linea.build/',
            'https://1rpc.io/linea',
        ],
        'chain_id': 59144,
        'gas_price_gwei': 2,
        'block_time_seconds': 3
    },
    'Sepolia': {
        'rpc_urls': [
            'https://eth-sepolia.g.alchemy.com/v2/gRVDFu74VYyCbIRzUncehA5i8tBkYbck',
            'https://1rpc.io/sepolia',
            'https://sepolia.infura.io',
        ],
        'chain_id': 11155111,
        'gas_price_gwei': 2,
        'block_time_seconds': 3
    },
    'Base': {
        'rpc_urls': [
            'https://base-rpc.publicnode.com',
            'https://1rpc.io/base',
            'https://base.drpc.org',
        ],
        'chain_id': 8453,
        'gas_price_gwei': 0.3,
        'block_time_seconds': 3
    }
}

# ERC-20 ABI
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]

def validate_address(address):
    """Validate if the address is a valid checksum address."""
    try:
        return Web3.is_checksum_address(address)
    except:
        return False

def get_balance(w3, address):
    """Check native token (BNB/ETH/MATIC) balance."""
    try:
        balance = w3.eth.get_balance(address)
        return balance
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        return 0

def transfer_native(w3, private_key, from_address, to_address, amount_wei, chain_id, gas_price_gwei):
    """Transfer native token (BNB/ETH/MATIC)."""
    try:
        nonce = w3.eth.get_transaction_count(from_address)
        gas_price = w3.to_wei(gas_price_gwei, 'gwei')
        gas_limit = 21000
        gas_cost = gas_limit * gas_price
        if amount_wei <= gas_cost:
            logger.error(f"Insufficient balance for gas: {w3.from_wei(amount_wei, 'ether')} < {w3.from_wei(gas_cost, 'ether')}")
            return None
        amount_to_send = amount_wei - gas_cost  # Subtract gas cost
        tx = {
            'nonce': nonce,
            'to': w3.to_checksum_address(to_address),
            'value': amount_to_send,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        }
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        logger.info(f"Native transaction sent: {tx_hash.hex()}")
        return tx_hash
    except Exception as e:
        logger.error(f"Error sending native transaction: {e}")
        return None

def transfer_erc20(w3, private_key, from_address, to_address, token_address, chain_id, gas_price_gwei):
    """Transfer ERC-20 tokens."""
    try:
        contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=ERC20_ABI)
        balance = contract.functions.balanceOf(from_address).call()
        if balance == 0:
            logger.info(f"No tokens to transfer for: {token_address}")
            return None

        nonce = w3.eth.get_transaction_count(from_address)
        gas_price = w3.to_wei(gas_price_gwei, 'gwei')
        gas_limit = 100000

        tx = contract.functions.transfer(
            w3.to_checksum_address(to_address),
            balance
        ).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': chain_id
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)  # Fixed: rawTransaction
        logger.info(f"ERC-20 transaction sent: {tx_hash.hex()} for token {token_address}")
        return tx_hash
    except Exception as e:
        logger.error(f"Error in ERC-20 transaction for {token_address}: {e}")
        return None

if __name__ == "__main__":
    # Load private key and safe wallet address
    private_key = os.getenv('COMPROMISED_PRIVATE_KEY')
    safe_address = os.getenv('SAFE_ADDRESS')
    token_addresses = os.getenv('TOKEN_ADDRESSES', '').split(',')
    active_chains = os.getenv('ACTIVE_CHAINS', 'bsc').split(',')

    if not private_key or not safe_address:
        logger.error("COMPROMISED_PRIVATE_KEY or SAFE_ADDRESS not set in .env file")
        exit(1)

    try:
        # Initialize Web3 instances and state for all chains
        chain_instances = {}
        for chain_name in active_chains:
            chain_name = chain_name.strip()  # Remove spaces
            if chain_name not in CHAINS:
                logger.error(f"Invalid chain: {chain_name}")
                continue
            w3 = None
            for rpc_url in CHAINS[chain_name]['rpc_urls']:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    logger.info(f"Connected to {chain_name}: {rpc_url}")
                    break
                logger.warning(f"Failed to connect to {chain_name} RPC: {rpc_url}")
            if w3 and w3.is_connected():
                chain_instances[chain_name] = {
                    'w3': w3,
                    'last_block': w3.eth.get_block_number(),
                    'chain_id': CHAINS[chain_name]['chain_id'],
                    'gas_price_gwei': CHAINS[chain_name]['gas_price_gwei'],
                    'block_time_seconds': CHAINS[chain_name]['block_time_seconds']
                }
            else:
                logger.error(f"Could not connect to {chain_name}")
                exit(1)

        account = w3.eth.account.from_key(private_key)
        compromised_address = account.address
    except Exception as e:
        logger.error(f"Invalid private key: {e}")
        exit(1)

    if not validate_address(safe_address):
        logger.error("Invalid safe wallet address")
        exit(1)

    logger.info(f"Starting rescue bot for compromised wallet: {compromised_address}")
    logger.info(f"Safe wallet: {safe_address}")
    logger.info(f"Active chains: {', '.join(chain_instances.keys())}")

    # Main loop: Check new blocks for each chain
    while True:
        try:
            for chain_name, chain_data in chain_instances.items():
                w3 = chain_data['w3']
                chain_id = chain_data['chain_id']
                gas_price_gwei = chain_data['gas_price_gwei']
                block_time_seconds = chain_data['block_time_seconds']

                current_block = w3.eth.get_block_number()
                if current_block > chain_data['last_block']:
                    logger.info(f"{chain_name}: New block detected: {current_block}")
                    chain_data['last_block'] = current_block

                    # Check native token (BNB/ETH/MATIC) balance
                    balance = get_balance(w3, compromised_address)
                    if balance > 0:
                        amount_to_send = balance  # Transfer the full balance
                        tx_hash = transfer_native(w3, private_key, compromised_address, safe_address, amount_to_send, chain_id, gas_price_gwei)
                        if tx_hash:
                            logger.info(f"{chain_name}: Waiting for native transaction {tx_hash.hex()} to confirm...")
                            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                            logger.info(f"{chain_name}: Native transfer successful")
                        else:
                            logger.error(f"{chain_name}: Native transfer failed")
                    else:
                        logger.info(f"{chain_name}: No native tokens to transfer")

                    # Check ERC-20 tokens
                    for token_address in token_addresses:
                        token_address = token_address.strip()
                        if not token_address:
                            continue
                        if not validate_address(token_address):
                            logger.error(f"{chain_name}: Invalid token address: {token_address}")
                            continue
                        tx_hash = transfer_erc20(w3, private_key, compromised_address, safe_address, token_address, chain_id, gas_price_gwei)
                        if tx_hash:
                            logger.info(f"{chain_name}: Waiting for ERC-20 transaction {tx_hash.hex()} to confirm...")
                            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                            logger.info(f"{chain_name}: ERC-20 transfer successful for {token_address}")
                        else:
                            logger.error(f"{chain_name}: ERC-20 transfer failed for {token_address}")

                time.sleep(block_time_seconds)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(10)  # Wait 10 seconds after an error
