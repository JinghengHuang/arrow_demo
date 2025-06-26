from service.base_service import BaseService
import service
import service.compute_grpc_service
import service.compute_julia_service
class ServiceFactory():
    """
    Service factory class, build service object based on parameter
    """
    
    def __init__(self):
        self._service_map = {
            "pyomo": service.compute_grpc_service.GrpcComputeService(),
            "julia": service.compute_julia_service.JuliaComputeService(),
        }
        pass
    
    def create_service(self, name: str) -> BaseService:
        try:
            if name is not None and name != "":
                return self._service_map[name]
        except:
            raise NameError()