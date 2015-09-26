import minsk.model as model
import minsk.eval.context as context


class TestUtilsMixin:
    @staticmethod
    def create_context(cards_str):
        cards = model.Card.parse_cards_line(cards_str)
        return context.EvalContext(*cards)
