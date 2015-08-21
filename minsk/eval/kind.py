from collections import defaultdict

import minsk.model


class FourEvaluator:
    def get_outs(self, *args):
        by_rank = defaultdict(list)
        for card in args:
            by_rank[card.rank].append(card)
        for rank, cards in by_rank.items():
            if len(cards) == 3:
                suit = set(minsk.model.Suit) - {card.suit for card in cards}
                return {minsk.model.Card(rank, suit.pop())}

    def find(self, *args):
        h1, h2 = args[0:2]
        by_rank = defaultdict(set)
        for card in args:
            by_rank[card.rank].add(card)
        for rank, cards in by_rank.items():
            if len(cards) == 4 and {h1, h2} & cards:
                return minsk.model.Hand.FOUR_OF_KIND, rank
            elif len(cards) == 3 and {h1, h2} & cards:
                return minsk.model.Hand.THREE_OF_KIND, rank
