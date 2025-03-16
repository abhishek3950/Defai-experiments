from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import Action
from src.almanak_library.models.params import ClosePositionParams
from src.almanak_library.enums import ActionType, Protocol

if TYPE_CHECKING:
    from ..strategy import StrategyUniV3SingleSidedETH


def teardown(strategy: "StrategyUniV3SingleSidedETH") -> ActionBundle:
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
    
    # Constants
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000006"
    
    close_params = ClosePositionParams(
        position_id=position_id,
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
    
    return ActionBundle(actions=[remove_liquidity_action])
