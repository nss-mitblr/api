class Student:
    fields = [
        "nss_id",
        "learner_id",
        "name",
        "reg_no",
        "volunteer_hours",
        "blood_type",
    ]

    def __init__(self, data):
        for idx, field in enumerate(self.fields):
            setattr(self, field, data[idx])

    def to_dict(self) -> dict:
        return {field: getattr(self, field) for field in self.fields}
