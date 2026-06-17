"""Tests for the observer/subject infrastructure.

These tests verify the Subject and Observer base classes and the EventType
enum that form the backbone of the model→view notification system.
"""
from __future__ import annotations

from typing import Any, List, Tuple

from OrecchietTetris.utils.observer_subject import Subject, Observer, EventType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class ConcreteObserver(Observer):
    """Minimal Observer that records every event it receives."""

    def __init__(self) -> None:
        self.received: List[Tuple[EventType, Any]] = []

    def update(self, event_type: EventType, data: Any) -> None:
        self.received.append((event_type, data))


# ---------------------------------------------------------------------------
# EventType
# ---------------------------------------------------------------------------

def test_event_type_has_all_expected_values() -> None:
    """All eight game events must be defined so the model and views agree."""
    names = {e.name for e in EventType}
    assert names == {
        "BOARD_UPDATED", "NEW_PIECE", "LINES_CLEARED",
        "SCORE_UPDATED", "GAME_OVER", "PAUSED", "RESUMED", "HOLD_UPDATED",
    }


def test_event_type_values_are_strings() -> None:
    for event in EventType:
        assert isinstance(event.value, str)


# ---------------------------------------------------------------------------
# Subject.attach
# ---------------------------------------------------------------------------

def test_attach_adds_observer() -> None:
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    assert observer in subject._observers


def test_attach_does_not_duplicate() -> None:
    """Attaching the same observer twice must not add it twice."""
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.attach(observer)
    assert subject._observers.count(observer) == 1


# ---------------------------------------------------------------------------
# Subject.detach  — covers lines 28-29
# ---------------------------------------------------------------------------

def test_detach_removes_attached_observer() -> None:
    """detach() must remove an observer that was previously attached."""
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.detach(observer)
    assert observer not in subject._observers


def test_detach_is_noop_for_unattached_observer() -> None:
    """detach() must silently ignore observers that are not attached."""
    subject = Subject()
    observer = ConcreteObserver()
    subject.detach(observer)  # must not raise


# ---------------------------------------------------------------------------
# Subject.notify
# ---------------------------------------------------------------------------

def test_notify_calls_update_on_all_observers() -> None:
    """All attached observers must receive the event."""
    subject = Subject()
    obs_a = ConcreteObserver()
    obs_b = ConcreteObserver()
    subject.attach(obs_a)
    subject.attach(obs_b)
    subject.notify(EventType.GAME_OVER)
    assert len(obs_a.received) == 1
    assert len(obs_b.received) == 1


def test_notify_delivers_correct_event_type_and_data() -> None:
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.notify(EventType.SCORE_UPDATED, 1234)
    event_type, data = observer.received[0]
    assert event_type is EventType.SCORE_UPDATED
    assert data == 1234


def test_notify_default_data_is_none() -> None:
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.notify(EventType.PAUSED)
    _, data = observer.received[0]
    assert data is None


def test_notify_does_not_reach_detached_observer() -> None:
    """An observer detached before notify must not receive the event."""
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.detach(observer)
    subject.notify(EventType.GAME_OVER)
    assert observer.received == []


def test_notify_with_no_observers_is_safe() -> None:
    subject = Subject()
    subject.notify(EventType.BOARD_UPDATED)  # must not raise


def test_multiple_events_are_all_delivered() -> None:
    subject = Subject()
    observer = ConcreteObserver()
    subject.attach(observer)
    subject.notify(EventType.NEW_PIECE, "piece")
    subject.notify(EventType.LINES_CLEARED, 4)
    assert len(observer.received) == 2
    assert observer.received[0][0] is EventType.NEW_PIECE
    assert observer.received[1][0] is EventType.LINES_CLEARED
