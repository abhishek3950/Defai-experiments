from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import SwapUniV3

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
    
    swap_action = SwapUniV3(
        token_in=USDC_ADDRESS,
        token_out=ETH_ADDRESS,
        amount_in=amount_to_swap,
        min_amount_out=0  # You might want to add slippage protection here
    )
    
    return ActionBundle(actions=[swap_action])
