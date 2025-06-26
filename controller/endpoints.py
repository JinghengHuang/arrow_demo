import json
from objects.util.response import Response
from typing import List, Dict, Optional, Union
from utils.mat_parser import load_model_from_mat
from objects.engine_model import EngineModel
from objects.solver_config import SolverConfig
import service
from service.service_factory import ServiceFactory
"""
Endpoints of all the exposed APIs, in logical layer
gRPC and potentially HTTP services all calls these to reduce duplication of efforts
"""
class Endpoint:
    def __init__(self):
        self.service_factory = ServiceFactory()
        pass
    def get_model_list(self, page: int = 0, result_per_page: int = 10) -> List[Dict]:
        """
        Retrieve a paginated list of saved models.

        :param page: Page number (default: 0)
        :param result_per_page: Number of models per page (default: 10)
        :return: List of model metadata
        """
        pass

    def get_recent_data_list(self) -> List[Dict]:
        """
        Retrieve a short list of recent cached data.

        :return: List of recent data metadata
        """
        pass

    def save_model(self, payload: Dict) -> Dict:
        """
        Save a new model or update an existing one.

        :param payload: Dict with fields `modelId`, `modelName`, `model`
        :return: Dict with saved model ID and status message
        """
        pass

    def delete_model(self, model_id: str) -> Dict:
        """
        Soft delete a model by model ID.

        :param model_id: The model ID to delete
        :return: Dict with deletion status message
        """
        pass

    def compute(self, payload: Dict) -> Dict:
        """
        Execute computation using a model and data, either from ID or inline.

        :param payload: Dict with fields:
            - modelId or model
            - dataId or data
            - dataName (optional)
        :return: Dict with result metadata and output
        """
        if payload['model'] is not None:
            service = self.service_factory.create_service(payload["engine"])
            params_str = payload.get("solver_params", None)
            solver = SolverConfig(
                solver_name=payload["solver_name"],
                solver_type=payload["solver_type"],
                params= json.loads(params_str) if params_str else None
            )           
            result = service.compute(payload['model'], solver)
        return result

    def compute_cobra(self, payload: Dict) -> Dict:
        """
        Execute a computation using a COBRA model, cached temporarily.

        :param payload: Dict with COBRA model JSON
        :return: Dict with result metadata and output
        """
        pass
    
    def parse_model(self, payload) -> Dict:
        """
        Parse a model from a file-like object.

        :param payload: Dict with fields:
            - modelId
            - modelName
            - model (file-like object)
        :return: Dict with parsed model metadata
        """
        return {"engine_model": load_model_from_mat(payload)}
        # pass