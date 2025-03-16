from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import SwapParams, Action
from src.almanak_library.enums import ActionType, Protocol, SwapSide

if TYPE_CHECKING:
    from ..strategy import MyStrategy

def swap_usdc_to_eth(strategy: "MyStrategy") -> ActionBundle:
    """
    Swaps half of USDC balance to ETH for providing liquidity.
    
    Steps:
    1. Gets current USDC balance
    2. Calculates amount to swap (half of balance)
    3. Creates swap action from USDC to ETH
    
    Returns:
        ActionBundle: Swap action for USDC to ETH
    """
    print("Swapping USDC to ETH")
    
    # Constants
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000000000006"
    
    # Get USDC balance
    usdc_balance = strategy.get_token_balance(USDC_ADDRESS)
    amount_to_swap = usdc_balance // 2  # Swap half the balance
    
    swap_params = SwapParams(
        side=SwapSide.SELL,
        tokenIn=USDC_ADDRESS,
        tokenOut=ETH_ADDRESS,
        fee=500,  # 0.05% fee tier
        recipient=strategy.wallet_address,
        amount=amount_to_swap,
        slippage=0.005  # 0.5% slippage
    )
    
    swap_action = Action(
        type=ActionType.SWAP,
        params=swap_params,
        protocol=Protocol.UNISWAP_V3
    )
    
    return ActionBundle(actions=[swap_action])
