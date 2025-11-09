# events.py - prosty bus zdarzeń dla Tkinter
class EventBus:
    def __init__(self):
        self._subs = {
            'employees_changed': [],   # dodanie/edycja/usunięcie, zmiana statusu/zmiany/maszyny
            'shifts_changed': [],      # zapis godzin zmian w Ustawieniach
            'absences_changed': [],    # dodanie/usunięcie/edycja urlopu/L4
        }
    def on(self, name, callback):
        if name in self._subs and callable(callback):
            self._subs[name].append(callback)
    def emit(self, name, *args, **kwargs):
        for cb in list(self._subs.get(name, [])):
            try:
                cb(*args, **kwargs)
            except Exception:
                pass
bus = EventBus()
