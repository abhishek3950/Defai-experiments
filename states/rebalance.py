from time import sleep, time
from typing import TYPE_CHECKING
from decimal import Decimal

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import RemoveLiquidityUniV3, AddLiquidityUniV3

if TYPE_CHECKING:
    from ..strategy import MyStrategy

def rebalance(strategy: "MyStrategy") -> ActionBundle:
    """
    Rebalances the position by:
    1. Removing current liquidity
    2. Providing new liquidity at current price ±2%
    
    Returns:
        ActionBundle: Actions for removing and adding liquidity
    """
    print("Rebalancing position")
    
    # Constants
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000006"
    PRICE_RANGE_MULTIPLIER = Decimal('0.02')  # 2% range
    
    # First, remove existing liquidity
    remove_liquidity_action = RemoveLiquidityUniV3(
        position_id=strategy.persistent_state.eth_usdc_position_id,
        amount_percentage=100  # Remove all liquidity
    )
    
    # Get current price and calculate new range
    current_price = strategy.get_current_eth_price()
    lower_price = current_price * (Decimal('1') - PRICE_RANGE_MULTIPLIER)
    upper_price = current_price * (Decimal('1') + PRICE_RANGE_MULTIPLIER)
    
    # After removal, get new balances
    eth_balance = strategy.get_token_balance(ETH_ADDRESS)
    usdc_balance = strategy.get_token_balance(USDC_ADDRESS)
    
    # Create new position
    add_liquidity_action = AddLiquidityUniV3(
        token0=ETH_ADDRESS,
        token1=USDC_ADDRESS,
        amount0=eth_balance,
        amount1=usdc_balance,
        lower_price=lower_price,
        upper_price=upper_price
    )
    
    # Update state
    strategy.persistent_state.last_eth_price = current_price
    strategy.persistent_state.last_rebalance_timestamp = time()
    
    return ActionBundle(actions=[remove_liquidity_action, add_liquidity_action])
