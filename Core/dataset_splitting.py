import os
import random
import shutil
import math


def split_dataset(dataset_path: str, prop: float, n_files: int = -1):
    """
    Arguments:
        dataset_path: path where the samples are found
        prop: proportion of files moved to train set 0 <= prop <= 1.0
        n_files: Number of files in the folder to be split and moved
        to the subsets

    Splits the dataset and train, test and validation set
    """
    dataset_path = os.path.join(dataset_path, "simulated_soundfields")

    if n_files == -1:
        n_files = len(
            [
                samples
                for samples in os.listdir(dataset_path)
                if samples.endswith(".mat")
            ]
        )

    for folder, files_moved in zip(
        ["train", "test", "val"],
        [prop * n_files, int(((1 - prop) / 2) * n_files), ((1 - prop) / 2) * n_files],
    ):

        samples = [
            samples for samples in os.listdir(dataset_path) if samples.endswith(".mat")
        ]
        random.shuffle(samples)

        destination = os.path.join(dataset_path, folder)
        i = 1
        for sample in samples:
            if i <= files_moved:
                shutil.move(
                    os.path.join(dataset_path, sample),
                    os.path.join(destination, sample),
                )
                i += 1
                print(i)

    print("Split Done")


def split_dataset_subfolders(dataset_path: str, n_files_sf: int):

    """
    Function to split the samples inside each subset to subfolder,
    in order to allow better addressing on each sample when being
    loaded on RAM
    """
    dataset_path = os.path.join(dataset_path, "simulated_soundfields")

    train_path = os.path.join(dataset_path, "train")
    test_path = os.path.join(dataset_path, "test")
    val_path = os.path.join(dataset_path, "val")

    # Checks how many subfolders are required on each subset
    file_n = len(
        [element for element in os.listdir(train_path) if element.endswith(".mat")]
    )
    n_subfolder = math.ceil(file_n / n_files_sf)
    train_sf = []
    for sf in range(n_subfolder):
        train_sf.append(f"ss{sf}")

    file_n = len(
        [element for element in os.listdir(test_path) if element.endswith(".mat")]
    )
    n_subfolder = math.ceil(file_n / n_files_sf)
    test_sf = []
    for sf in range(n_subfolder):
        test_sf.append(f"ss{sf}")

    file_n = len(
        [element for element in os.listdir(val_path) if element.endswith(".mat")]
    )
    n_subfolder = math.ceil(file_n / n_files_sf)
    val_sf = []
    for sf in range(n_subfolder):
        val_sf.append(f"ss{sf}")

    # Creates subfolders if it does not exist
    for subset, set_path in zip(
        [train_sf, test_sf, val_sf], [train_path, test_path, val_path]
    ):
        for sf in subset:
            if not os.path.exists(os.path.join(set_path, sf)):
                os.makedirs(os.path.join(set_path, sf), exist_ok=False)

    # Moves the samples to the subfolders
    for source, sub_folders_list in zip(
        [train_path, test_path, val_path], [train_sf, test_sf, val_sf]
    ):

        samples = [
            samples for samples in os.listdir(source) if samples.endswith(".mat")
        ]
        random.shuffle(samples)
        sf_iter = iter(sub_folders_list)
        i = 1
        sub_folder_name = next(sf_iter)

        for sample in samples:

            if i > n_files_sf:
                i = 1
                sub_folder_name = next(sf_iter)

            i += 1
            destination = os.path.join(source, sub_folder_name)
            shutil.move(os.path.join(source, sample), os.path.join(destination, sample))

        remaining_files = [
            mat_file for mat_file in os.listdir(source) if mat_file.endswith(".mat")
        ]

        if len(remaining_files) != 0:
            for mat_file in remaining_files:
                destination = os.path.join(source, "ss0")
                shutil.move(
                    os.path.join(source, mat_file),
                    os.path.join(destination, mat_file),
                )

    print("Sets splitted in subfolders")
