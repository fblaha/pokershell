from collections import defaultdict

from minsk.model import Suit, Card


class FourEvaluator:
    def get_outs(self, *args):
        by_rank = defaultdict(list)
        for card in args:
            by_rank[card.rank].append(card)
        for rank, cards in by_rank.items():
            if len(cards) == 3:
                suit = set(Suit) - {card.suit for card in cards}
                return {Card(rank, suit.pop())}
