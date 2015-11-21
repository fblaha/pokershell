import pokershell.utils as utils


class ConfigOption(utils.CommonReprMixin):
    def __init__(self, name, type, value, short, description):
        super().__init__()
        self.name = name
        self.type = type
        self._value = value
        self.short = short
        self.description = description

    @property
    def value(self):
        return self._value

    @property
    def python_name(self):
        return self.name.replace('-', '_')

    @property
    def long(self):
        return '--' + self.name

    @value.setter
    def value(self, val):
        if type(val) != self.type:
            self._value = self.type(val)
        else:
            self._value = val


options = {}


def register_option(name, type, value, short, description):
    option = ConfigOption(name, type, value, short, description)
    assert name not in options
    options[name] = option
    return option


player_num = register_option(name='player-num', value=2, type=int, short='-p',
                             description='default player number used when actual player '
                                         'number is specified in hand simulation')
hand_stats = register_option(name='hand-stats', value=3, type=int, short='-x',
                             description='length of hand statistics table')
