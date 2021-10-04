import abc


class DbalServiceError(RuntimeError):
    pass


class DbalService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, sentence: str, **parameters):
        raise NotImplementedError
