class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, event_type, data=None):
        for observer in self._observers:
            observer.update(event_type, data)


class Observer:
    def update(self, event_type, data):
        pass # Da implementare nelle sottoclassi