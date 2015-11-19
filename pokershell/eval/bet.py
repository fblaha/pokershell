class BetAdviser:
    @staticmethod
    def get_equity(hand_strength, pot):
        try:
            return hand_strength * pot
        except ZeroDivisionError:
            return float('inf')
