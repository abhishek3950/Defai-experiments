from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models.action import Action
from src.almanak_library.models.params import SwapParams
from src.almanak_library.enums import ActionType, Protocol, SwapSide, ExecutionStatus

if TYPE_CHECKING:
    from ..strategy import StrategyUniV3SingleSidedETH

def swap_usdc_to_eth(strategy: "StrategyUniV3SingleSidedETH") -> ActionBundle:
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

def validate_swap_usdc_to_eth(strategy: "StrategyUniV3SingleSidedETH") -> bool:
    """
    Validates the swap execution and checks the results.
    """
    actions = strategy.executioner_status["actions"]
    
    # Check overall status
    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed: Expected SUCCESS, Received: {actions.status}")
    
    # Find the swap action
    swap_actions = [action for action in actions.actions if action.type == ActionType.SWAP]
    if len(swap_actions) != 1:
        raise ValueError(f"Expected 1 swap action, received: {len(swap_actions)}")
    
    # Get execution details
    swap_executed = swap_actions[0].get_execution_details()
    if not swap_executed:
        raise ValueError("No receipt found for swap")
        
    # Verify tokens
    if swap_executed.tokenIn_symbol.lower() != "usdc" or swap_executed.tokenOut_symbol.lower() != "weth":
        raise ValueError("Swap executed for wrong tokens")
        
    print(f"Swap validated successfully: {swap_executed.amountIn} USDC -> {swap_executed.amountOut} ETH")
    return True

def sadflow_swap_usdc_to_eth(strategy: "StrategyUniV3SingleSidedETH") -> ActionBundle:
    """
    Handles failed swap transactions by retrying with updated parameters.
    """
    actions = strategy.executioner_status["actions"]
    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            print("Swap failed, retrying with updated parameters...")
            # Increase slippage for retry
            strategy.persistent_state.retry_count = strategy.persistent_state.retry_count + 1
            if strategy.persistent_state.retry_count > 3:
                raise ValueError("Max retry attempts reached")
            return swap_usdc_to_eth(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow called with SUCCESS status")
        case _:
            raise ValueError(f"Invalid status: {actions.status}")
