import csv

global names
names = []

def is_valid_name(name: str) -> bool:
    for num in range(0, 10):
        if str(num) in name:
            return False

    if all([not char.isalpha() for char in name]):
        return False

    return True

def add_food(name: str):
    global names

    for name in name.split('/'):
        name = name.strip().lower()
        if not name in names and is_valid_name(name):
            names += [name]

csvs = [
    # filename, column
    ('./inputs/generic-food.csv', 0),
    #('./inputs/dishes.txt', -1)
]

for filename, column in csvs:
    with open(filename) as csvfile:
        foodreader = csv.reader(csvfile)
        for i, row in enumerate(foodreader):
            if i != 0:
                food = row[column]

                if '(' in food:
                    out_of_parens, in_parens = food.replace(')', '').split('(')

                    add_food(out_of_parens)

                    for item in in_parens.split(','):
                        if not '.' in item:
                            add_food(item)
                else:
                    add_food(food)

newline_separated_files = [
    "./inputs/food.txt",
    "./inputs/food.txt.1",
    "./inputs/ingredients.txt"
]

for filename in newline_separated_files:
    with open(filename) as file:
        for line in file.read().strip().split():
            add_food(line)

print(repr(names))
print(len(names))

with open('foods.txt', 'w') as f:
    for name in names:
        print(name, file=f)
