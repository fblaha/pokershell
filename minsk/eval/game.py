class GameState:
    def __init__(self, cards, player_num, pot):
        super().__init__()
        self._cards = cards
        self._player_num = player_num
        self._pot = pot

    def is_successor(self, other):
        my_cards = ''.join(map(repr, self._cards))
        other_cards = ''.join(map(repr, other._cards))
        return my_cards.startswith(other_cards) \
               and self._pot >= other._pot \
               and self._player_num <= other._player_num
