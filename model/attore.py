from dataclasses import dataclass
@dataclass
class Attore:
    id : str
    name : str
    height : int
    date_of_birth : str
    known_for_movies : str

    def __str__(self):
        return f"{self.id} - {self.name}; (codice: {self.height})"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id