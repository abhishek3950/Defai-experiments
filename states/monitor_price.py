from time import sleep, time
from typing import TYPE_CHECKING
from decimal import Decimal

from src.strategy.models import ActionBundle

if TYPE_CHECKING:
    from ..strategy import MyStrategy

def monitor_price(strategy: "MyStrategy") -> bool:
    """
    Monitors ETH price and determines if rebalancing is needed.
    
    Rebalancing conditions:
    1. Price deviation > strategy threshold: Immediate rebalance
    2. Price deviation > min threshold and interval passed: Periodic rebalance
    
    Returns:
        bool: True if rebalance is needed, None otherwise
    """
    print("Monitoring ETH price")
    
    current_price = strategy.get_current_eth_price()
    current_time = time()
    
    # Store price in history
    strategy.persistent_state.price_history.append({
        'price': current_price,
        'timestamp': current_time
    })
    
    # Get initial position price
    initial_price = strategy.persistent_state.last_eth_price
    if not initial_price:
        strategy.persistent_state.last_eth_price = current_price
        strategy.persistent_state.last_rebalance_timestamp = current_time
        return None
    
    # Calculate price deviation
    price_deviation = abs(current_price - initial_price) / initial_price
    time_since_last_rebalance = current_time - strategy.persistent_state.last_rebalance_timestamp
    
    # Check rebalancing conditions
    if price_deviation > strategy.PRICE_DEVIATION_THRESHOLD:
        print(f"Price deviation {price_deviation:.2%} exceeds {strategy.PRICE_DEVIATION_THRESHOLD:.1%} threshold. Rebalancing needed.")
        return True
        
    if time_since_last_rebalance >= strategy.REBALANCE_INTERVAL and price_deviation > strategy.MIN_PRICE_DEVIATION:
        print(f"Periodic check: Price deviation {price_deviation:.2%} exceeds {strategy.MIN_PRICE_DEVIATION:.1%} threshold. Rebalancing needed.")
        return True
    
    print(f"No rebalancing needed. Current deviation: {price_deviation:.2%}")
    return None
