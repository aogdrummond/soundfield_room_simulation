from Core.dataset_creation import create_rectangular_sample, create_dataset


if __name__ == "__main__":

    dataset_path = r"C:\Users\aledr\Desktop\teste\general\Comparação\\"

    create_dataset(
        geometry="general",
        dataset_path=dataset_path,
        n_samples=10,
    )
