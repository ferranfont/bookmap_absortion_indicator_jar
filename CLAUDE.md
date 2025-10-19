# Development Log - Bookmap Absorption Indicator

## Project Overview

This indicator was developed to detect volume absorption patterns in Bookmap, specifically designed for identifying long entry opportunities by tracking buy/sell imbalances and volume spikes.

## Key Design Decisions

### 1. Volume Attribution
- `is_bid = True` → Green bubbles (aggressive buying, hitting ASK)
- `is_bid = False` → Red bubbles (aggressive selling, hitting BID)
- Initially confused, corrected through testing with visual confirmation

### 2. Indicator Architecture

**big_bid (Red)**
- Uses `deque(maxlen=20)` for efficient rolling window
- Only counts BID volume (red bubbles/aggressive sells)
- Provides context for absorption detection

**real_delta (Grey)**
- Continuous accumulation: `ask_volume - bid_volume`
- Never resets, shows long-term market bias
- Foundation for understanding overall flow

**imbalance (Green)**
- Clone of real_delta but resets on volume spikes
- Key innovation: allows tracking fresh accumulation after absorption
- Resets when spike detected (volume ≥ 2x average of last 14 trades)

### 3. Spike Detection Logic

```python
# Calculate average of last 14 trades
recent_volumes = list(bid_volume_window[alias])[-SPIKE_AVG_WINDOW:]
avg_volume = sum(recent_volumes) / len(recent_volumes)

# Detect spike
if size >= avg_volume * SPIKE_MULTIPLIER:
    spike_detected = True
```

- Uses last 14 trades from the 20-trade window
- 2x multiplier balances sensitivity vs noise
- Only triggers on BID volume (red bubbles)

## Performance Optimizations

1. **Single pass processing**: All indicators calculated in one trade handler
2. **Efficient data structures**: deque for O(1) append and automatic size limiting
3. **Minimal state**: Only tracks necessary accumulation counters
4. **No CSV logging**: Removed to prevent I/O bottlenecks

## Evolution of the Code

### Version 1: Initial attempt
- Multiple indicators (3 separate overlays)
- Too complex, caused Bookmap to freeze
- Used time-based windows (problematic)

### Version 2: Simplified
- Removed time-based logic
- Single trade-based accumulation
- Still had performance issues with overlays

### MVP v1: Working version
- Moved all indicators to BOTTOM panel
- Simplified to 2 indicators (volume + delta)
- Stable performance

### Current (v1.1): Feature complete
- Added spike detection and reset logic
- 3 indicators with clear purposes
- Visual spike markers (pending)

## Challenges Overcome

1. **is_bid confusion**: Bookmap's parameter naming is counterintuitive
   - Solution: Empirical testing with visual confirmation

2. **Performance**: Initial versions crashed Bookmap
   - Solution: Removed CSV, simplified calculations, optimized data structures

3. **Overlay rendering**: OVERLAY type draws continuous lines, not points
   - Solution: All indicators in BOTTOM panel where line charts work well

4. **Reset logic**: Need to detect spike BEFORE accumulating new volume
   - Solution: Check spike condition before updating accumulators

## Future Enhancements (Ideas)

1. ✅ Visual markers on spike detection
2. Separate indicators for long/short setups
3. Configurable parameters via Bookmap UI
4. Alert system for significant imbalances
5. Volume profile integration

## Technical Notes

### Why rolling window for big_bid?
- Provides recent context without infinite accumulation
- 20 trades ≈ 10-30 seconds depending on market activity
- Allows comparison of current volume to recent baseline

### Why separate spike detection window?
- 14 trades provides stable average
- Smaller than display window (20) to focus on recent activity
- Prevents single outlier from skewing average too much

### Color choices
- Red: Selling pressure (intuitive)
- Grey: Neutral accumulation (doesn't bias interpretation)
- Green: Reset tracking (indicates fresh opportunity)

## Code Quality Notes

- Clear variable naming (ask_volume, bid_volume, etc.)
- Parameterized constants at top of file
- Comments explain "why" not just "what"
- Separation of concerns (handlers, indicators, detection logic)

## Testing Approach

All testing done live with Bookmap:
1. Visual confirmation of volume attribution (bubbles vs lines)
2. Performance testing (no lag, smooth rendering)
3. Logic verification (spike detection timing)
4. Edge cases (empty windows, first trades)

## Lessons Learned

1. **Bookmap API limitations**: OVERLAY doesn't support discrete markers well
2. **Performance matters**: Real-time trading requires efficient code
3. **Simple is better**: Complex features often don't add value
4. **Visual feedback crucial**: Trader needs immediate visual confirmation
5. **Test with real data**: Synthetic testing doesn't catch UI/performance issues
