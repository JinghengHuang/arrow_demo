from abc import ABC, abstractmethod

class ArrowModel(ABC):
    def to_pydict(self) -> dict:
        """
        Convert the model to a dictionary of Arrow-compatible components.
        Subclasses can override if custom logic is needed.
        """
        self.sanity_check()
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith("_") and v is not None
        }

    @abstractmethod
    def sanity_check(self) -> None:
        """
        Perform consistency and validity checks on the model.
        Should raise ValueError or TypeError if checks fail.
        """
        pass
