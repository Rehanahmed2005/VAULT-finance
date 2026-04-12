from datetime import datetime 

class Transaction:
    def __init__(self, trans_type, amount, category, note, date=None):
        self.trans_type = trans_type
        self.amount = amount
        self.category = category
        self.note = note
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            "trans_type": self.trans_type,
            "amount": self.amount,
            "category": self.category,
            "note":self.note,
            "date": self.date
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            trans_type=data["trans_type"],
            amount=data["amount"],
            category=data["category"],
            note=data["note"],
            date=data.get("date")
        )