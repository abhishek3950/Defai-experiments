import os

from src.almanak_library.models.action_bundle import ActionBundle
from src.almanak_library.models import (
    PersistentState,
    State,
    StrategyConfig,
    SubState,
)
from src.almanak_library.strategy_base import StrategyUniV3
from src.almanak_library.protocols.uniswap_v3 import UniswapV3
from src.utils.utils import get_protocol_sdk, get_web3_by_network_and_chain

from .states.initialization import initialization
from .states.teardown import teardown
from .states.swap_usdc_to_eth import swap_usdc_to_eth
from .states.provide_liquidity import provide_liquidity
from .states.monitor_price import monitor_price
from .states.rebalance import rebalance


class MyStrategy(StrategyUniV3):
    STRATEGY_NAME = "Single_Sided_ETH_USDC_UniV3_Base"
    PRICE_DEVIATION_THRESHOLD = 0.02  # 2% threshold for immediate rebalance
    MIN_PRICE_DEVIATION = 0.005      # 0.5% minimum deviation for hourly rebalance
    REBALANCE_INTERVAL = 3600        # 1 hour in seconds
    
    # Token addresses
    USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    ETH_ADDRESS = "0x4200000000000000000000000000000006"

    def __init__(self, **kwargs):
        """
        Initialize the strategy with given configuration parameters.

        Args:
            **kwargs: Strategy-specific configuration parameters.
        """
        super().__init__()
        self.name = self.STRATEGY_NAME.replace("_", " ")

        # Overwrite the States and SubStates for this Strategy
        self.State = State
        self.SubState = SubState

        # Get configuration from kwargs
        try:
            self.config = StrategyConfig(**kwargs)
        except Exception as e:
            raise ValueError(f"Invalid Strategy Configuration. {e}")

        self.id = self.config.id
        self.chain = self.config.chain
        self.network = self.config.network
        self.protocol = self.config.protocol
        self.pool_address = self.config.pool_address

        # Initialize web3 and protocol SDK
        self.web3 = get_web3_by_network_and_chain(self.network, self.chain)
        self.uniswap_v3 = get_protocol_sdk(self.protocol, self.network, self.chain)

        self.initialize_persistent_state()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"chain={self.chain}, network={self.network}, protocol={self.protocol}, "
            f"wallet_address={self.wallet_address}, mode={self.mode})"
        )

    @classmethod
    def get_persistent_state_model(cls):
        return PersistentState

    @classmethod
    def get_config_model(cls):
        return StrategyConfig

    def initialize_persistent_state(self):
        """
        Initialize the persistent state by uploading the JSON template.
        """
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            "persistent_state_template.json",
        )
        super().initialize_persistent_state(template_path)

    def restart_cycle(self) -> None:
        """A Strategy should only be restarted when the full cycle is completed."""
        if self.persistent_state.current_state == self.State.COMPLETED:
            # Properly restart the cycle
            self.persistent_state.current_flowstatus = (
                self.InternalFlowStatus.PREPARING_ACTION
            )
            # Insert the necessary logic to restart the cycle here.
            # self.persistent_state.current_state = self.State.COMPLETED
            self.persistent_state.completed = False

            # Dump the state to the persistent state because we load it when called.
            self.save_persistent_state()
        elif self.persistent_state.current_state == self.State.TERMINATED:
            print("Strategy is terminated, nothing to restart.")
        else:
            raise ValueError("The strategy is not completed yet, can't restart.")

    def run(self):
        """
        Executes the strategy by progressing through its state machine based on the current state.

        This method orchestrates the transitions between different states of the strategy,
        performing actions as defined in each state, and moves to the next state based on the
        actions' results and strategy's configuration.

        Returns:
            dict: A dictionary containing the current state, next state, and actions taken or
                recommended, depending on the execution mode.

        Raises:
            ValueError: If an unknown state is encountered, indicating a potential issue in state management.

        Notes:
            - This method is central to the strategy's operational logic, calling other methods
            associated with specific states like initialization, rebalancing, or closing positions.
            - It integrates debugging features to display balances and positions if enabled.
        """
        print("Running the strategy")
        if self.config.pause_strategy:
            print("Strategy is paused.")
            return None

        try:
            self.load_persistent_state()
        except Exception as e:
            raise ValueError(f"Unable to load persistent state. {e}")

        if self.config.initiate_teardown and (
            self.persistent_state.current_state in [
                self.State.COMPLETED,
                self.State.MONITOR_PRICE
            ]
        ):
            self.persistent_state.current_state = self.State.TEARDOWN
            self.persistent_state.current_flowstatus = self.InternalFlowStatus.PREPARING_ACTION

        print(self.persistent_state)

        actions = None
        while self.is_locked and not actions:
            match self.persistent_state.current_state:
                case State.INITIALIZATION:
                    actions = initialization(self)
                    self.persistent_state.current_state = State.SWAP_USDC_TO_ETH
                
                case State.SWAP_USDC_TO_ETH:
                    actions = swap_usdc_to_eth(self)
                    self.persistent_state.current_state = State.PROVIDE_LIQUIDITY
                
                case State.PROVIDE_LIQUIDITY:
                    actions = provide_liquidity(self)
                    self.persistent_state.current_state = State.MONITOR_PRICE
                
                case State.MONITOR_PRICE:
                    actions = monitor_price(self)
                    if actions:  # If rebalance is needed
                        self.persistent_state.current_state = State.REBALANCE
                
                case State.REBALANCE:
                    actions = rebalance(self)
                    self.persistent_state.current_state = State.MONITOR_PRICE
                
                case State.TEARDOWN:
                    actions = teardown(self)
                    self.persistent_state.current_state = State.TERMINATED
                
                case State.TERMINATED:
                    print("Strategy is terminated.")
                    actions = None
                
                case _:
                    raise ValueError(f"Unknown state: {self.persistent_state.current_state}")

        if actions is None:
            self.persistent_state.current_actions = []
        elif isinstance(actions, ActionBundle):
            self.persistent_state.current_actions = [actions.id]
        else:
            raise ValueError(f"Invalid actions type. {type(actions)} : {actions}")

        self.save_persistent_state()
        return actions

    def complete(self) -> None:
        self.persistent_state.current_state = self.State.COMPLETED
        self.persistent_state.current_flowstatus = (
            self.InternalFlowStatus.PREPARING_ACTION
        )
        self.persistent_state.completed = True

    def log_strategy_balance_metrics(self, action_id: str):
        """Logs strategy balance metrics per action. It is called in the StrategyBase class."""
        pass

    def get_usdc_balance(self) -> int:
        return self.get_token_balance(self.USDC_ADDRESS)

    def get_eth_balance(self) -> int:
        return self.get_token_balance(self.ETH_ADDRESS)

    def get_token_balance(self, token_address: str) -> int:
        """Get the balance of a token for the strategy's wallet address."""
        return self.uniswap_v3.get_token_balance(token_address, self.wallet_address)

    def get_current_eth_price(self) -> float:
        """Get the current ETH price from the pool."""
        return self.uniswap_v3.get_pool_spot_rate(self.pool_address)

    def get_active_position_info(self, position_id: int) -> tuple:
        """Get information about an active liquidity position."""
        return self.uniswap_v3.get_position_info(position_id)
