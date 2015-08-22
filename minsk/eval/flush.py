import minsk.eval as eval


class FlushEvaluator(eval.AbstractEvaluator):
    def find(self, context):
        by_suit = context.by_suit
        sorted_sets = sorted(by_suit.values(), key=len, reverse=True)
        if sorted_sets:
            biggest = sorted_sets[0]
            if len(biggest) >= 5:
                card_rank = lambda card: card.rank
                sorted_cards = sorted(biggest, key=card_rank, reverse=True)[0:5]
                return [card.rank for card in sorted_cards]
