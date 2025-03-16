from time import sleep
from typing import TYPE_CHECKING
from decimal import Decimal

from src.strategy.models import ActionBundle, AddLiquidityUniV3

if TYPE_CHECKING:
    from ..strategy import MyStrategy

def provide_liquidity(strategy: "MyStrategy") -> ActionBundle:
    """
    Provides liquidity to Uniswap V3 ETH-USDC pool with ±2% price range.
    
    Steps:
    1. Gets current ETH and USDC balances
    2. Gets current ETH price
    3. Calculates price range (±2% from current price)
    4. Creates add liquidity action
    
    Returns:
        ActionBundle: Add liquidity action for Uniswap V3
    """
    print("Providing liquidity to Uniswap V3 ETH-USDC pool")
    
    # Constants
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000006"
    PRICE_RANGE_MULTIPLIER = Decimal('0.02')  # 2% range
    
    # Get current ETH price and balances
    current_price = strategy.get_current_eth_price()
    eth_balance = strategy.get_token_balance(ETH_ADDRESS)
    usdc_balance = strategy.get_token_balance(USDC_ADDRESS)
    
    # Calculate price range (±2%)
    lower_price = current_price * (Decimal('1') - PRICE_RANGE_MULTIPLIER)
    upper_price = current_price * (Decimal('1') + PRICE_RANGE_MULTIPLIER)
    
    add_liquidity_action = AddLiquidityUniV3(
        token0=ETH_ADDRESS,
        token1=USDC_ADDRESS,
        amount0=eth_balance,
        amount1=usdc_balance,
        lower_price=lower_price,
        upper_price=upper_price
    )
    
    return ActionBundle(actions=[add_liquidity_action])
