class BetAdviser:
    @staticmethod
    def get_max_bet(hand_strength, pot):
        return hand_strength * pot / (1 - hand_strength)
