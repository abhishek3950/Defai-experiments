from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, validator
from web3 import Web3
from src.almanak_library.enums import Chain, Network, Protocol
from src.strategy.models import PersistentStateBase, StrategyConfigBase, InternalFlowStatus


class State(Enum):
    """Enum representing the state of the strategy."""
    INITIALIZATION = "INITIALIZATION"
    SWAP_USDC_TO_ETH = "SWAP_USDC_TO_ETH"
    PROVIDE_LIQUIDITY = "PROVIDE_LIQUIDITY"
    MONITOR_PRICE = "MONITOR_PRICE"
    REBALANCE = "REBALANCE"
    COMPLETED = "COMPLETED"
    TEARDOWN = "TEARDOWN"
    TERMINATED = "TERMINATED"


class SubState(Enum):
    """Enum representing the substates of some of the strategy states."""
    NO_SUBSTATE = "NO_SUBSTATE"


class Cosigner(BaseModel):
    name: str = "NONE"


class InitializationConfig(BaseModel):
    initial_token: str
    initial_amount_usdc: str
    fee_tier: int

    @validator("initial_token")
    def validate_ethereum_address(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return v


class PersistentState(PersistentStateBase):
    current_state: State
    current_substate: SubState
    current_flowstatus: InternalFlowStatus
    current_actions: List[UUID] = []
    sadflow_counter: int = 0
    sadflow_actions: List[UUID] = []
    not_included_counter: int = 0
    position_id: int = -1
    retry_count: int = 0
    rebalance_history: List[Dict] = []
    last_check_time: Optional[datetime] = None
    last_rebalance_time: Optional[datetime] = None
    last_eth_price: Optional[float] = None
    price_history: List[Dict] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["current_state"] = self.current_state.value
        data["current_substate"] = self.current_substate.value
        data["current_flowstatus"] = self.current_flowstatus.value
        data["current_actions"] = [str(action) for action in self.current_actions]
        data["sadflow_actions"] = [str(action) for action in self.sadflow_actions]
        if self.last_rebalance_time:
            data["last_rebalance_time"] = self.last_rebalance_time.isoformat()
        if self.last_check_time:
            data["last_check_time"] = self.last_check_time.isoformat()
        return data


class StrategyConfig(StrategyConfigBase):
    network: Network
    chain: Chain
    protocol: Protocol
    pool: str
    type: str = "CONCENTRATED_LIQUIDITY"
    cosigner: Cosigner
    data_source: str = "COINGECKO_DEX"
    max_sadflow_retries: int = 3
    max_not_included_retries: int = 5
    initiate_teardown: bool = False
    pause_strategy: bool = False
    pool_address: str
    rebalance_interval: int = 3600
    granularity: str = "15m"
    time_window: int = 96
    initialization: InitializationConfig

    @validator("pool_address")
    def validate_ethereum_address(cls, v):
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return v

    def model_dump(self, *args, **kwargs):
        d = super().model_dump(*args, **kwargs)
        d["network"] = self.network.value
        d["chain"] = self.chain.value
        d["protocol"] = self.protocol.value
        d["initialization"] = self.initialization.model_dump()
        return d
