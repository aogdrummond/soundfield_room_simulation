from Core.dataset_creation import create_rectangular_room, create_dataset
from Core.dataset_splitting import split_dataset, split_dataset_subfolders
import json

if __name__ == "__main__":

    config_path = r"soundfield_room_simulation\config_femder.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    config["dataset"]["name"] = "new_dataset"
    dataset_path = "".join(
        [config["storage"]["path"], "/datasets/", config["dataset"]["name"]]
    )
    # create_dataset(geometry="general", dataset_path=dataset_path, n_samples=7)
    # split_dataset(dataset_path=dataset_path, prop=0.5, n_files=7)
    # split_dataset_subfolders(dataset_path=dataset_path, n_files_sf=1)
