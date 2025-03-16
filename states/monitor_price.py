from datetime import datetime
import pytz
from typing import TYPE_CHECKING, Dict, Any, List
from time import time
from src.almanak_library.enums import ExecutionStatus, ActionType

if TYPE_CHECKING:
    from ..strategy import StrategyUniV3SingleSidedETH

def monitor_price(strategy: "StrategyUniV3SingleSidedETH") -> bool:
    """
    Enhanced price monitoring with position-aware bounds and time-based checks.
    """
    print("Monitoring ETH price and position")
    
    # Get current state
    current_time = datetime.now(pytz.utc)
    spot_price = strategy.uniswap_v3.get_pool_spot_rate(strategy.pool_address)
    
    # Get position info if active
    if strategy.persistent_state.position_id != -1:
        pos_info = strategy.get_active_position_info(strategy.persistent_state.position_id)
        pos_lower = strategy.uniswap_v3.tick_to_price(pos_info[5])
        pos_upper = strategy.uniswap_v3.tick_to_price(pos_info[6])
        
        # Check if price is outside position bounds
        if spot_price < pos_lower or spot_price > pos_upper:
            log_rebalance_metrics(strategy, {
                'trigger': 'position_bounds',
                'current_price': spot_price,
                'lower_bound': pos_lower,
                'upper_bound': pos_upper
            })
            return True
    
    # Time-based check
    if strategy.persistent_state.last_rebalance_time:
        time_passed = current_time - strategy.persistent_state.last_rebalance_time
        if time_passed.total_seconds() > strategy.REBALANCE_INTERVAL:
            log_rebalance_metrics(strategy, {
                'trigger': 'time_interval',
                'time_passed': time_passed,
                'interval': strategy.REBALANCE_INTERVAL
            })
            return True
    
    # Store state for next check
    strategy.persistent_state.last_eth_price = spot_price
    strategy.persistent_state.last_check_time = current_time
    
    print(f"No rebalancing needed. Price: {spot_price}")
    return False

def log_rebalance_metrics(strategy: "StrategyUniV3SingleSidedETH", details: Dict[str, Any]) -> None:
    """
    Logs detailed metrics about rebalancing triggers and conditions.
    """
    print("\n=== Rebalance Triggered ===")
    print(f"Trigger: {details['trigger']}")
    
    if 'current_price' in details:
        print(f"Current Price: {details['current_price']}")
        print(f"Position Bounds: {details['lower_bound']} - {details['upper_bound']}")
    
    if 'time_passed' in details:
        print(f"Time Since Last Rebalance: {details['time_passed']}")
        print(f"Rebalance Interval: {details['interval']} seconds")
    
    print(f"Wallet Balance ETH: {strategy.get_eth_balance()}")
    print(f"Wallet Balance USDC: {strategy.get_usdc_balance()}")
    print("==========================\n")
    
    # Store metrics in persistent state for analysis
    if not hasattr(strategy.persistent_state, 'rebalance_history'):
        strategy.persistent_state.rebalance_history = []
    
    strategy.persistent_state.rebalance_history.append({
        'timestamp': datetime.now(pytz.utc),
        'trigger': details['trigger'],
        'details': details
    })
