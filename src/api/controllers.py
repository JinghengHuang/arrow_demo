"""
Controller for interacting with the service to perform computations.
"""
from typing import Dict
import pyarrow as pa
from service.model_service.model_factory import ModelFactory
from service.optimization_service.opt_service_factory import OptServiceFactory
from utils.dict_to_pa_table import dict_to_pa_table


class Controller:
    """
    Controller class interacts with the service layer to execute computations
    using the provided data.
    """
    def __init__(self):
        self.service_factory = OptServiceFactory()
        self.model_factory = ModelFactory()


    def compute(self, payload) -> Dict:
        """
        Execute computation using provided data.

        Args:
            payload (pa.Table): input data as a PyArrow table.
            
        Returns:
            Tuple[bool, pa.RecordBatch]: success flag and result as a PyArrow RecordBatch 
            or error message.
        
        Raises:
            ValueError: if the payload is invalid.
            KeyError: if required columns are missing in the payload.
        """
        engine = payload.column("engine")[0].as_py()
        optimization_service = self.service_factory.create_service(engine)
        solver_model = self.model_factory.create_model("solver", payload.column("solver")[0].as_py())
        model_name = payload.column("model_name")[0].as_py()
        data_model = self.model_factory.create_model(
            solver_model.solver_type.lower(),
            payload.column("model")[0].as_py()
        )
        result = optimization_service.compute(data_model, solver_model, model_name)
        if result.column("success")[0].as_py():
            return True, result
        return False, pa.RecordBatch.from_pydict({
                "error_message": [result.column("error_message")[0].as_py()]
            })
