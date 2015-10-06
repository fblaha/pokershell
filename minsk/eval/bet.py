import math


class BetAdviser:
    @staticmethod
    def get_max_bet(hand_strength, pot, card_num=7):
        if card_num >= 6:
            return hand_strength * pot / (1 - hand_strength)
        elif card_num == 5:
            turn_strength = 1 - math.sqrt(1 - hand_strength)
            return turn_strength * pot / (1 - turn_strength)
