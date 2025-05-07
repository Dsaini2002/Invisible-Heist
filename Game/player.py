class Player:
    def __init__(self, position):
        self.position = position
        self.transport_history = []
        self.location_history = []

        # Each player starts with a set number of tickets
        self.tickets = {
            'taxi': 10,
            'bus': 8,
            'underground': 4,
            'black': 0  # MrX-only ticket
        }

    def move(self, to, transport):
        if not self.has_ticket(transport):
            raise ValueError(f"No {transport} tickets left.")
        self.position = to
        self.transport_history.append(transport)
        self.location_history.append(to)
        self.tickets[transport] -= 1

    def get_visible_position(self):
        return self.position

    def has_ticket(self, transport):
        return self.tickets.get(transport, 0) > 0

    def get_tickets(self):
        return dict(self.tickets)


class MrX(Player):
    def __init__(self, position, num_truns_to_reveal=3):
        super().__init__(position)
        self.tickets['black'] = 5  # MrX has 5 black tickets
        self.num_truns_to_reveal = num_truns_to_reveal  # Number of turns until MrX reveals his position
        self.role = "Mr. X"
        self.num_moves = 0

    def move(self, to, transport):
        if not self.has_ticket(transport):
            raise ValueError(f"No {transport} tickets left.")
        self.num_moves += 1
        if (self.num_moves) % self.num_truns_to_reveal == 0:
            self.location_history.append(self.position)
        else:
            self.location_history.append(-1)
        self.position = to
        self.transport_history.append(transport)
        self.tickets[transport] -= 1

class Detective(Player):
    def __init__(self, role, position):
        super().__init__(position)
        self.role = role
        self.tickets['black'] = 0  # Detectives can't use black tickets