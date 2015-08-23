import minsk.model as model
import minsk.eval.context as context


class TestUtilsMixin:
    @staticmethod
    def parse_cards(cards_line):
        cards_str = cards_line.split()
        cards = [model.Card.parse(card) for card in cards_str]
        if len(cards) != len(set(cards)):
            raise ValueError('Duplicate cards: {0}'.format(cards_line))
        return cards

    def create_context(self, cards_str):
        cards = self.parse_cards(cards_str)
        return context.EvalContext(*cards)
