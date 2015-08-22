class FlushEvaluator:
    def find(self, context):
        by_suit = context.by_suit
        sorted_sets = sorted(by_suit.values(), key=len, reverse=True)
        if sorted_sets:
            biggest = sorted_sets[0]
            if len(biggest) >= 5:
                sorted_cards = sorted(biggest, key=lambda card: card.rank, reverse=True)
                return [card.rank for card in sorted_cards]
