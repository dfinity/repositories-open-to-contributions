def check_sort():
    with open("open-repositories.txt") as my_file:
        data = my_file.read()
        repo_list = data.replace("\n", " ").split(".")
        print(repo_list)
        print(sorted(repo_list))
        if repo_list != sorted(repo_list):
            raise Exception("open-repositories.txt is not correctly sorted")


if __name__ == "__main__":
    check_sort()
