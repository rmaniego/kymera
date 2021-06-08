import os

def get_filenames(path, extensions=[]):
    filenames = []
    print(extensions)
    for filepath in os.listdir(path):
        if filepath.split(".")[-1].lower() in extensions:
            filenames.append(filepath)
    return filenames

aggregated = ""
filenames = get_filenames("python", ["txt"])
for filename in filenames:
    with open(f"python/{filename}", "r", encoding="utf-8") as file:
        aggregated += "\n"
        aggregated += file.read()

with open("python.txt", "w+", encoding="utf-8") as file:
    file.write(aggregated)
