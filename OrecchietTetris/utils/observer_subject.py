from typing import List, Any


class Subject:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, event_type: str, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event_type, data)


class Observer:
    def update(self, event_type: str, data: Any) -> None:
        pass  # Da implementare nelle sottoclassi
