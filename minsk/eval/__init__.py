from abc import ABCMeta, abstractmethod


class AbstractEvaluator(metaclass=ABCMeta):
    required_rank_counts = set()
    required_suit_count = 1

    @abstractmethod
    def find(self, context):
        pass
