from Core.dataset_creation import create_rectangular_sample, create_dataset


if __name__ == "__main__":

    dataset_path = r"C:\Users\aledr\Desktop\teste\general\Comparação\\"
    room_dim = [3, 6, 2.4]
    source_position = [0, 3, 1.2]
    create_rectangular_sample(
        room_dim=room_dim, source_position=source_position, view_soundfield=True
    )
    # create_dataset(
    #     geometry="general",
    #     dataset_path=dataset_path,
    #     n_samples=10,
    # )
