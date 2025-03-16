from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import RemoveLiquidityUniV3

if TYPE_CHECKING:
    from ..strategy import MyStrategy


def teardown(strategy: "MyStrategy") -> ActionBundle:
    """
    Concludes the strategy by removing liquidity from Uniswap V3 pool.
    
    Steps:
    1. Checks if we have an active position
    2. Removes liquidity if position exists
    
    Returns:
        ActionBundle: Remove liquidity actions if position exists
    """
    print("Tearing down the strategy")
    
    position_id = strategy.persistent_state.eth_usdc_position_id
    if not position_id:
        print("No active position to close")
        return None
    
    remove_liquidity_action = RemoveLiquidityUniV3(
        position_id=position_id,
        amount_percentage=100  # Remove all liquidity
    )
    
    return ActionBundle(actions=[remove_liquidity_action])
