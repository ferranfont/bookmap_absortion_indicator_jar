# Bookmap Absorption Indicator

An advanced volume analysis indicator for Bookmap that detects absorption patterns and volume imbalances in real-time.

## Features

### Indicators

1. **big_bid** (Red line)
   - Shows cumulative BID volume (aggressive sells) over a rolling window of last 20 trades
   - Helps identify selling pressure

2. **real_delta** (Dark grey line)
   - Cumulative delta: ASK volume - BID volume
   - Never resets, shows overall market bias
   - Positive = more buying, Negative = more selling

3. **imbalance** (Green line)
   - Same as real_delta but resets to 0 when a volume spike is detected
   - Helps identify absorption zones and new accumulation/distribution phases
   - Visual marker appears on spike detection

### Spike Detection

A spike occurs when:
- A single trade's volume ≥ 2x the average of the last 14 trades
- When detected, the green "imbalance" indicator resets to 0
- Useful for identifying significant market moves or absorption

## Parameters

Configurable in lines 5-7 of `hello_world.py`:

```python
WINDOW_SIZE = 20         # Rolling window for big_bid calculation
SPIKE_MULTIPLIER = 2.0   # Multiplier for spike detection (2x average)
SPIKE_AVG_WINDOW = 14    # Number of trades to calculate average for spike
```

## Installation

1. Copy `hello_world.py` to your Bookmap Python directory
2. In Bookmap: Settings → API → Python
3. Click "Add" and select `hello_world.py`
4. Enable the checkbox next to the script
5. Open a chart - indicators will appear in the bottom panel

## Usage

### Interpreting the Indicators

**For Long Entries:**
- Watch for green "imbalance" line rising (more buying than selling)
- Red "big_bid" spikes indicate large sell orders being absorbed
- When imbalance resets after a spike, it shows fresh accumulation starting

**Volume Spike Reset:**
- When you see the green line drop to 0, a large volume spike occurred
- This often indicates absorption at support levels
- New accumulation phase begins after reset

## Technical Details

- **ASK volume**: Aggressive buying (hitting the ask) - Green bubbles in Bookmap
- **BID volume**: Aggressive selling (hitting the bid) - Red bubbles in Bookmap
- All indicators update in real-time with each trade
- Uses efficient deque data structure for rolling windows

## Version

Current: MVP v1.1

## Requirements

- Bookmap with Python API enabled
- Python 3.x
- Bookmap Python SDK (included with Bookmap)

## Author

Created with Claude Code
