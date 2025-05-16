# FundGuard

A blockchain monitoring and fund interception tool designed to track scammer wallets and redirect funds to a secure address. Supports Ethereum, Binance Smart Chain (BSC), Polygon, Arbitrum, and Solana.

**Features**:
- **Supported Chains**: Ethereum, BSC, Polygon, Arbitrum, Solana.
- **Seed Phrase Monitoring**: Derives wallet addresses from a seed phrase.
- **Automatic Transfer**: Redirects incoming funds to a specified wallet.
- **Periodic Execution**: Runs every 10 seconds to monitor transactions.

---

## Prerequisites
- [Node.js](https://nodejs.org/) (v16+ recommended)
- npm or yarn
- A `.env` file with the scammer’s seed phrase and your wallet addresses

## Setup
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/your-username/FundGuard.git
   cd FundGuard