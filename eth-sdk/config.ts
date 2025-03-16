import { defineConfig } from "@gnosis-guild/eth-sdk";

export default defineConfig({
  contracts: {
    mainnet: {
      dai: "0x6b175474e89094c44da98b954eedeac495271d0f",
    },
    base: {
      eth: "0x4200000000000000000000000000000000000006",
      usdc: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    },
  },
  // Add RPC URLs for better ABI fetching
  rpc: {
    base: "https://mainnet.base.org",
  }
});