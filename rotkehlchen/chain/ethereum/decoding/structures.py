from typing import Dict, NamedTuple, Optional, Tuple

from rotkehlchen.accounting.structures.base import (
    HistoryBaseEntry,
    HistoryEventSubType,
    HistoryEventType,
)
from rotkehlchen.assets.asset import Asset
from rotkehlchen.fval import FVal


class ActionItem(NamedTuple):
    """Action items to propagate to other decoders during decoding"""
    action: str
    sequence_index: int
    from_event_type: HistoryEventType
    from_event_subtype: HistoryEventSubType
    asset: Asset
    amount: FVal
    to_event_type: Optional[HistoryEventType] = None
    to_event_subtype: Optional[HistoryEventSubType] = None
    to_notes: Optional[str] = None
    to_counterparty: Optional[str] = None
    extra_data: Optional[Dict] = None
    # Optional event data that pairs it with the event of the action item
    # Contains a tuple with the paired event and whether it's an out event (True) or in event
    paired_event_data: Optional[Tuple[HistoryBaseEntry, bool]] = None
