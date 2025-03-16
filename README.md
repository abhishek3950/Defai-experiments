# UniV3 Single-Sided ETH Liquidity Strategy

An Almanak strategy for providing single-sided ETH liquidity on Uniswap V3 (Base Chain).

## Strategy Overview

This strategy automates the process of providing liquidity to the ETH-USDC pool on Uniswap V3:

1. Start with USDC
2. Swap 50% to ETH
3. Provide liquidity in ±2% range around current price
4. Monitor price movements
5. Rebalance when:
   - Price deviates > 2% (immediate rebalance)
   - Price deviates > 0.5% and 1 hour passed (periodic rebalance)

## Setup

1. Install Almanak
2. Configure environment variables
3. Deploy strategy:
```bash
almanak strat push
```

## Configuration

The strategy uses the following parameters:
- Price range: ±2% around current price
- Rebalance thresholds:
  - Immediate: 2% deviation
  - Periodic: 0.5% deviation after 1 hour
- Token addresses (Base Chain):
  - USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
  - ETH: `0x4200000000000000000000000000000006`

## States

1. `initialization.py`: Setup approvals and initial state
2. `swap_usdc_to_eth.py`: Convert 50% USDC to ETH
3. `provide_liquidity.py`: Create UniV3 position
4. `monitor_price.py`: Track price movements
5. `rebalance.py`: Adjust position when needed
6. `teardown.py`: Remove liquidity and clean up