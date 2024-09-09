class Event:
    fields = [
        "event_id",
        "event_name",
        "event_date",
        "event_time",
        "venue",
        "hours",
    ]

    def __init__(self, data):
        for idx, field in enumerate(self.fields):
            setattr(self, field, data[idx])

    def to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.fields}
