import csv


def load_household_data(path):
    result = {}
    with open(path, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            # convert all strings to an integer
            [year, min_age, max_age, size, count] = list(map(int, row))

            # create result entries if they do not exist
            if year not in result:
                result[year] = {}
            if (min_age, max_age) not in result[year]:
                result[year][(min_age, max_age)] = {}

            result[year][(min_age, max_age)][size] = count

        return result
