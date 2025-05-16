module.exports = {
    networks: [
        // Mainnets
        {
            name: "Ethereum",
            rpc: "https://ethereum.publicnode.com",
            symbol: "ETH",
            isTestnet: false
        },
        {
            name: "Binance Smart Chain",
            rpc: "https://bsc-dataseed.binance.org/",
            symbol: "BNB",
            isTestnet: false
        },
        {
            name: "Polygon",
            rpc: "https://polygon-rpc.com/",
            symbol: "MATIC",
            isTestnet: false
        },
        {
            name: "Arbitrum",
            rpc: "https://arb1.arbitrum.io/rpc",
            symbol: "ETH",
            isTestnet: false
        },
        // Testnets
        {
            name: "Sepolia",
            rpc: "https://rpc.sepolia.org",
            symbol: "ETH",
            isTestnet: true
        },
        {
            name: "BSC Testnet",
            rpc: "https://data-seed-prebsc-1-s1.binance.org:8545/",
            symbol: "BNB",
            isTestnet: true
        },
        {
            name: "Sahara AI Testnet",
            rpc: "https://313313.rpc.thirdweb.com",
            symbol: "SAH",
            isTestnet: true,
            chainId: 313313
        },
        {
            name: "Monad Testnet",
            rpc: "https://twilight-billowing-sanctuary.monad-testnet.quiknode.pro/6547815a8037d76c299730063824da15da96cfa6",
            symbol: "MON",
            isTestnet: true
        }
    ],
    tokens: {
        // Mainnets
        "Ethereum": [
            {
                name: "USDT",
                address: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                decimals: 6
            }
        ],
        "Binance Smart Chain": [
            {
                name: "USDT",
                address: "0x55d398326f99059fF775485246999027B3197955",
                decimals: 18
            }
        ],
        "Polygon": [],
        "Arbitrum": [],
        // Testnets
        "Sepolia": [],
        "BSC Testnet": [],
        "Sahara AI Testnet": [],
        "Monad Testnet": [
            {
                name: "MON",
                address: "0xF323dcDe4d33efe83cf455F78F9F6cc656e6B659",
                decimals: 18
            }
        ]
    }
};