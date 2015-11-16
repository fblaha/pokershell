import re

import pokershell.eval.game as game
import pokershell.model as model

NUM_RE = '\d+(\.(\d+)?)?'
CARD_RE = '([2-9tjqka][hscd])+'


class LineParser:
    @classmethod
    def parse_state(cls, line):
        cards, player_nums, pots = cls._parse_raw(line)
        pot = pots[-1] if pots else None
        player_num = player_nums[-1] if player_nums else None
        return game.GameState(model.Card.parse_cards(cards), player_num, pot)

    @staticmethod
    def _parse_raw(line):
        tokens = line.replace(';', ' ').split()
        cards = [token for token in tokens
                 if re.fullmatch(CARD_RE, token, re.IGNORECASE)]
        joined = ''.join(cards)
        cards = list(zip(joined[::2], joined[1::2]))
        params = [token for token in tokens if re.fullmatch(NUM_RE, token)]
        pots = [float(param) for param in params if '.' in param]
        player_nums = [int(param) for param in params if '.' not in param]
        return cards, player_nums, pots

    @classmethod
    def parse_history(cls, line):
        chunks = cls._split_line(line)
        last_state = None
        for i in range(1, len(chunks) + 1):
            history_line = ' '.join(chunks[:i])
            state = cls.parse_state(history_line)
            if last_state:
                state.previous = last_state
            last_state = state
        return last_state

    @staticmethod
    def _split_line(line):
        return [token.strip() for token in line.split(';') if token.strip()]

    @staticmethod
    def validate_syntax(line):
        line = line.replace(';', ' ')
        return all(re.fullmatch(NUM_RE, token) or
                   re.fullmatch(CARD_RE, token, re.IGNORECASE)
                   for token in line.split())

    @classmethod
    def validate_semantics(cls, line):
        errors = []
        cards_str, player_nums, pots = cls._parse_raw(line)
        cards = model.Card.parse_cards(cards_str)
        if len(cards) != len(set(cards)):
            errors.append('Duplicate cards: {0}'.format(cards))
        card_num = len(cards_str)
        if not 2 <= card_num <= 7:
            errors.append('Card number is expected to be '
                          'between 2 and 7 (both included). Actual is %d' % card_num)
        if any(a > b for a, b in zip(pots, pots[1:])):
            errors.append('Pot size decay : %s' % pots)
        if any(a < b for a, b in zip(player_nums, player_nums[1:])):
            errors.append('Player number raised: %s' % player_nums)
        for chunk in cls._split_line(line):
            _, player_nums, pots = cls._parse_raw(chunk)
            if len(pots) > 1:
                errors.append('Ambiguous pot specification %s' % pots)
            if len(player_nums) > 1:
                errors.append('Ambiguous player number specification %s' % player_nums)
            for player_num in player_nums:
                if not 2 <= player_num <= 10:
                    errors.append('Player number is expected to be between '
                                  '2 and 10 (both included). Actual is %d' % player_num)
        return errors
