class BetAdviser:
    @staticmethod
    def get_equity(hand_strength, pot):
        try:
            return hand_strength * pot / (1 - hand_strength)
        except ZeroDivisionError:
            return float('inf')
