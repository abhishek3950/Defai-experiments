from time import sleep
from typing import TYPE_CHECKING

from src.strategy.models import ActionBundle, ApproveToken

if TYPE_CHECKING:
    from ..strategy import MyStrategy


def initialization(strategy: "MyStrategy") -> ActionBundle:
    """
    Initializes the strategy by checking USDC balance and setting up approvals.
    
    Steps:
    1. Checks USDC balance
    2. Approves USDC spending for Uniswap V3 Router
    3. Sets up initial state variables
    
    Returns:
        ActionBundle: Approval actions for USDC
    """
    print("Initializing Single Sided ETH-USDC UniV3 Strategy")
    
    # Constants
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    UNIV3_ROUTER = "0x2626664c2603336E57B271c5C0b26F421741e481"
    
    # Check USDC balance
    usdc_balance = strategy.get_token_balance(USDC_ADDRESS)
    print(f"Initial USDC balance: {usdc_balance}")
    
    if usdc_balance <= 0:
        raise ValueError("No USDC balance available for strategy initialization")
    
    # Initialize persistent state variables
    strategy.persistent_state.last_eth_price = None
    strategy.persistent_state.last_rebalance_timestamp = None
    strategy.persistent_state.eth_usdc_position_id = None
    strategy.persistent_state.price_history = []
    
    # Create approval action for USDC
    approve_action = ApproveToken(
        token_address=USDC_ADDRESS,
        spender=UNIV3_ROUTER,
        amount=usdc_balance
    )
    
    return ActionBundle(actions=[approve_action])
