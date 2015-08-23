import minsk.model as model
import minsk.eval.context as context


class TestUtilsMixin:
    @staticmethod
    def parse_combo(line):
        cards_str = line.split()
        return [model.Card.parse(card) for card in cards_str]

    def create_context(self, cards_str):
        parsed = self.parse_combo(cards_str)
        return context.EvalContext(*parsed)
