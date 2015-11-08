import re

import minsk.eval.game as game
import minsk.model as model

NUM_RE = '\d+(\.(\d+)?)?'
CARD_RE = '([2-9tjqka][hscd])+'


class LineParser:
    @staticmethod
    def parse_state(line):
        tokens = line.split()
        cards = [token for token in tokens
                 if re.fullmatch(CARD_RE, token, re.IGNORECASE)]
        params = [token for token in tokens if re.fullmatch(NUM_RE, token)]
        joined = ''.join(cards)
        cards = zip(joined[::2], joined[1::2])
        pot, player_num = None, None
        for param in params:
            if '.' in param:
                pot = float(param)
            else:
                player_num = int(param)
                assert 2 <= player_num <= 10
        return game.GameState(model.Card.parse_cards(cards), player_num, pot)

    @classmethod
    def parse_history(cls, line):
        chunks = [token.strip() for token in line.split(';') if token.strip()]
        last_state = None
        for i in range(1, len(chunks) + 1):
            history_line = ' '.join(chunks[:i])
            state = cls.parse_state(history_line)
            if last_state:
                state.previous = last_state
            last_state = state
        return last_state

    @staticmethod
    def validate_syntax(line):
        line = line.replace(';', ' ')
        return all(re.fullmatch(NUM_RE, token) or
                   re.fullmatch(CARD_RE, token, re.IGNORECASE)
                   for token in line.split())
