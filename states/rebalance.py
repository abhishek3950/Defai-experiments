from time import sleep, time
from typing import TYPE_CHECKING
from decimal import Decimal

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import Action
from src.almanak_library.models.params import ClosePositionParams, OpenPositionParams
from src.almanak_library.enums import ActionType, Protocol

if TYPE_CHECKING:
    from ..strategy import StrategyUniV3SingleSidedETH

def rebalance(strategy: "StrategyUniV3SingleSidedETH") -> ActionBundle:
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
    close_params = ClosePositionParams(
        position_id=strategy.persistent_state.eth_usdc_position_id,
        recipient=strategy.wallet_address,
        token0=ETH_ADDRESS,
        token1=USDC_ADDRESS,
        slippage=0.005  # 0.5% slippage
    )
    
    remove_liquidity_action = Action(
        type=ActionType.CLOSE_LP_POSITION,
        params=close_params,
        protocol=Protocol.UNISWAP_V3
    )
    
    # Get current price and calculate new range
    current_price = strategy.get_current_eth_price()
    lower_price = current_price * (Decimal('1') - PRICE_RANGE_MULTIPLIER)
    upper_price = current_price * (Decimal('1') + PRICE_RANGE_MULTIPLIER)
    
    # After removal, get new balances
    eth_balance = strategy.get_token_balance(ETH_ADDRESS)
    usdc_balance = strategy.get_token_balance(USDC_ADDRESS)
    
    # Create new position
    open_position_params = OpenPositionParams(
        token0=ETH_ADDRESS,
        token1=USDC_ADDRESS,
        fee=500,  # 0.05% fee tier
        price_lower=float(lower_price),
        price_upper=float(upper_price),
        amount0_desired=eth_balance,
        amount1_desired=usdc_balance,
        recipient=strategy.wallet_address,
        slippage=0.005  # 0.5% slippage
    )
    
    add_liquidity_action = Action(
        type=ActionType.OPEN_LP_POSITION,
        params=open_position_params,
        protocol=Protocol.UNISWAP_V3
    )
    
    # Update state
    strategy.persistent_state.last_eth_price = current_price
    strategy.persistent_state.last_rebalance_timestamp = time()
    
    return ActionBundle(actions=[remove_liquidity_action, add_liquidity_action])
