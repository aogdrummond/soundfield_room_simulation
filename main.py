from Core.dataset_creation import create_dataset
from Core.dataset_splitting import split_dataset, split_dataset_subfolders
import json
import os

if __name__ == "__main__":
    """
    geometry: geometry of sample to be created (either "general" or "rectangular")
    n_samples: number of samples to be created
    prop: proportion of total samples to be used as train set
    n_files_sf: number of files inside each subfolder 
    
    """
    #Parameters
    geometry =  "general"
    n_samples = 100
    prop = 0.7
    n_files_sf = 15

    config_path = r"config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    config["dataset"]["name"] = "new_general_dataset"
    dataset_path = os.path.join(
        config["storage"]["path"], "datasets", config["dataset"]["name"]
    )

    create_dataset(geometry=geometry, dataset_path=dataset_path, n_samples=n_samples)
    split_dataset(dataset_path=dataset_path, prop=prop)
    split_dataset_subfolders(dataset_path=dataset_path, n_files_sf=n_files_sf)
