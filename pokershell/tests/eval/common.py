import pokershell.eval.context as context
import pokershell.model as model


class TestUtilsMixin:
    @staticmethod
    def create_context(cards_str):
        cards = model.Card.parse_cards_line(cards_str)
        return context.EvalContext(*cards)
