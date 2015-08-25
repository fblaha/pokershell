import minsk.model as model
import minsk.eval.context as context


class TestUtilsMixin:

    def create_context(self, cards_str):
        cards = model.Card.parse_cards(cards_str)
        return context.EvalContext(*cards)
