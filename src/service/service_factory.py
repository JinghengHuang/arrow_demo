"""
    Service factory class, build service object based on parameter
"""
from service.base_service import BaseService
from service.compute_grpc_service import GrpcComputeService
from service.compute_julia_service import JuliaComputeService


class ServiceFactory():
    """
    Service factory class, build service object based on parameter
    This class provides a method to create a service instance based on the engine type.
    It maintains a mapping of engine names to service instances.
    """

    def __init__(self):
        self._service_map = {
            "pyomo": GrpcComputeService(),
            "julia": JuliaComputeService(),
        }

    def create_service(self, name: str) -> BaseService:
        """Create a type of concrete service

        Args:
            name (str): Name of the service

        Raises:
            NameError: Wrong service name or name is empty

        Returns:
            BaseService: Service instance of a type determined by name
        """
        if name is not None and name != "":
            return self._service_map[name]
        raise NameError(f"Service name '{name}' is not recognized or is empty.")
