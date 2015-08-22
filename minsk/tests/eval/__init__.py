import minsk.eval.context as context
import minsk.model as model


def create_context(cards_str):
    parsed = model.Card.parse_combo(cards_str)
    return context.EvalContext(*parsed)
