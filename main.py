import os

hypotheses = ["hypothesis1"] #, "hypothesis2", "hypothesis3", "hypothesis4", "construction_exploration", "misc"]

for dir_name in hypotheses:
    files = os.listdir("policies/{}".format(dir_name))
    for file_name in files:
        if file_name == "__init__.py" or file_name == "__pycache__":
            continue

        print("Running {}/{}".format(dir_name, file_name))
        os.system("python policies/{}/{}".format(dir_name, file_name))
