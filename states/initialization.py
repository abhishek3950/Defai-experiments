from time import sleep
from typing import TYPE_CHECKING

from src.almanak_library.enums import ActionType, Protocol
from src.almanak_library.models.action import Action
from src.almanak_library.models.params import ApproveParams
from src.almanak_library.models.action_bundle import ActionBundle

if TYPE_CHECKING:
    from ..strategy import StrategyUniV3SingleSidedETH


def initialization(strategy: "StrategyUniV3SingleSidedETH") -> ActionBundle:
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
    approve_params = ApproveParams(
        token_address=USDC_ADDRESS,
        spender_address=UNIV3_ROUTER,
        from_address=strategy.wallet_address,
        amount=usdc_balance
    )
    
    approve_action = Action(
        type=ActionType.APPROVE,
        params=approve_params,
        protocol=Protocol.UNISWAP_V3
    )
    
    return ActionBundle(actions=[approve_action])
