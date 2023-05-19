def check_sort(filename: str) -> None:
    with open(filename) as my_file:
        data = my_file.read()
        repo_list = data.split("\n")
        repo_list.remove("")
        if repo_list != sorted(repo_list):
            raise Exception(f"{filename} is not correctly sorted")


if __name__ == "__main__":
    check_sort("open-repositories.txt")
