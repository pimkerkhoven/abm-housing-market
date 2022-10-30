import csv


def load_money_data(path):
    result = {}
    with open(path, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            # Convert all strings to number.
            # Convert to float if string contains a '.', else convert to an int
            [year, min_age, max_age, percentage, mean, median] = list(map(
                lambda value: float(value) if "." in value else int(value), row))

            # create result entries if they do not exist
            if year not in result:
                result[year] = {}
            if (min_age, max_age) not in result[year]:
                result[year][(min_age, max_age)] = []

            result[year][(min_age, max_age)].append((percentage, mean, median))

        return result
