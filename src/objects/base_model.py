"""
Base model class for Arrow-compatible models
"""
from abc import ABC, abstractmethod


class ArrowModel(ABC):
    """
    ArrowModel: Base class for Arrow-compatible optimization models
    This class provides a common interface for optimization models that can be
    serialized to and from Arrow's in-memory format.
    It defines methods for converting the model to a dictionary representation
    and performing consistency checks.
    Subclasses should implement the `sanity_check` and `from_dict` methods
    to handle specific model types.
    """
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
        raise NotImplementedError("Subclasses must implement sanity_check method")
