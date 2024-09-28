from datetime import timedelta
from dataclasses import dataclass, field
from collections import OrderedDict

@dataclass
class Timeframe:
    lable: str
    value: timedelta = field(default_factory=timedelta)
    
available_timeframes = OrderedDict([
    ("1m", Timeframe("1m", timedelta(minutes=1))),
    ("5m", Timeframe("5m", timedelta(minutes=5))),
    ("15m", Timeframe("15m", timedelta(minutes=15))),
    ("30m", Timeframe("30m", timedelta(minutes=30))),
    ("1H", Timeframe("1H", timedelta(hours=1))),
    ("4H", Timeframe("4H", timedelta(hours=4))),
    ("1D", Timeframe("1D", timedelta(days=1))),
    ("1W", Timeframe("1W", timedelta(weeks=1))),
])