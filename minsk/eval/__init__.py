from abc import ABCMeta, abstractmethod


class AbstractEvaluator(metaclass=ABCMeta):
    @abstractmethod
    def find(self, context):
        pass
