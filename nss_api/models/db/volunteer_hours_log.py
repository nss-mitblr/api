class Volunteer_Log:
    fields = [
        "event_id",
        "volunteer_id",
        "hours",
        "reason",
    ]

    def __init__(self, data):
        for idx, field in enumerate(self.fields):
            setattr(self, field, data[idx])

    def to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.fields}
