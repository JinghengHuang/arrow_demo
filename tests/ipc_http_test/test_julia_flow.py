import requests



def test_julia_flow():
    # Upload the .mat file to server
    url = "http://127.0.0.1:8000/compute"
    mat_file_path = "sample/e_coli_core.mat"
    files = {
        'model': ('e_coli_core.mat', open(mat_file_path, 'rb'),  "application/octet-stream")
    }
    params = {
        "model_name": "e_coli_core",
        "engine": "julia",
        "solver_name": "Highs",
        "solver_type": "LP",
        "solver_params": '{"presolve": true, "dual": true, "primal": true}'
    }
    req = requests.post(url, files=files, data=params)
    print(req.content)
    
    
if __name__ == "__main__":
    test_julia_flow()