def detect_candlestick_patterns(df):
    """
    Example: Detect simple bullish engulfing patterns.
    Returns a boolean series marking pattern presence.
    """
    engulfing = ((df['close'] > df['open'].shift(1)) &
                 (df['open'] < df['close'].shift(1)) &
                 (df['close'].shift(1) < df['open'].shift(1)))
    return engulfing.astype(int)
