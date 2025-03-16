from enum import Enum

from src.almanak_library.enums import Chain, Network, Protocol
from src.strategy.models import PersistentStateBase, StrategyConfigBase


class State(Enum):
    """Enum representing the state of the strategy."""

    INITIALIZATION = "INITIALIZATION"
    SWAP_USDC_TO_ETH = "SWAP_USDC_TO_ETH"
    PROVIDE_LIQUIDITY = "PROVIDE_LIQUIDITY"
    MONITOR_PRICE = "MONITOR_PRICE"
    REBALANCE = "REBALANCE"
    COMPLETED = "COMPLETED"  # A "Cycle" is completed in between Checks for Rebalance
    TEARDOWN = "TEARDOWN"
    TERMINATED = "TERMINATED"  # The Strategy is terminated


class SubState(Enum):
    """Enum representing the substates of some of the strategy states. A state machine within a state machine."""

    NO_SUBSTATE = "NO_SUBSTATE"


class PersistentState(PersistentStateBase):
    current_state: State
    current_substate: SubState


class StrategyConfig(StrategyConfigBase):
    id: str
    network: Network
    chain: Chain
    protocol: Protocol
    initiate_teardown: bool
    pause_strategy: bool
