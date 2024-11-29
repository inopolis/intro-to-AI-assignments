import copy
import random

# def read_puzzle_console():
#     """
#     Читает судоку из консоли. Пользователь должен ввести 9 строк, каждая из 9 элементов,
#     разделённых пробелами. Используйте '-' или '0' для пустых ячеек.
#     """
#     # print("Введите судоку по 9 элементов в каждой строке, разделённых пробелами.")
#     # print("Используйте '-' или '0' для пустых ячеек.")
#     puzzle = []
#     for i in range(9):
#         while True:
#             try:
#                 line = input().strip().split()
#                 if len(line) != 9:
#                     raise ValueError("Каждая строка должна содержать ровно 9 элементов.")
#                 row = []
#                 for val in line:
#                     if val == "-" or val == "0":
#                         row.append(0)
#                     else:
#                         num = int(val)
#                         if num < 1 or num > 9:
#                             raise ValueError("Числа должны быть от 1 до 9.")
#                         row.append(num)
#                 puzzle.append(row)
#                 break
#             except ValueError as ve:
#                 print(f"Ошибка: {ve}. Пожалуйста, введите строку заново.")
#     return puzzle

# Закомментировано: чтение из файла
def read_puzzle(filename):
    puzzle = []
    with open(filename, "r") as f:
        for line in f:
            row = []
            for val in line.strip().split():
                if val == "-" or val == "0":
                    row.append(0)
                else:
                    row.append(int(val))
            puzzle.append(row)
    return puzzle

# def write_solution_console(solution):
#     """
#     Выводит решение судоку в консоль в требуемом формате.
#     """
#     for row in solution:
#         print(" ".join(str(val) for val in row))

# Закомментировано: запись в файл
def write_solution(solution, filename):
    with open(filename, "w") as f:
        for i, row in enumerate(solution):
            line = " ".join(str(val) for val in row)
            f.write(line)
            f.write("\n")  # Ensure ending with a new line character

def print_puzzle(puzzle):
    for row in puzzle:
        print(" ".join(str(val) if val != 0 else "_" for val in row))

def fitness(individual):
    score = 0
    # Row fitness
    for row in individual:
        score += 9 - len(set(row))
    # Column fitness
    for col in zip(*individual):
        score += 9 - len(set(col))
    # Subgrid fitness
    for i in range(3):
        for j in range(3):
            block = []
            for x in range(3):
                for y in range(3):
                    block.append(individual[3 * i + x][3 * j + y])
            score += 9 - len(set(block))
    return score

def create_individual(puzzle, fixed_cells):
    individual = []
    for i in range(9):
        nums = [n for n in range(1, 10) if n not in puzzle[i]]
        random.shuffle(nums)
        row = []
        idx = 0
        for j in range(9):
            if fixed_cells[i][j]:
                row.append(puzzle[i][j])
            else:
                if idx < len(nums):
                    row.append(nums[idx])
                    idx += 1
                else:
                    # Если не хватает чисел, заполнить случайным образом (может привести к дубликатам)
                    row.append(random.randint(1, 9))
        individual.append(row)
    return individual
    

def mutate(individual, fixed_cells):
    row = random.randint(0, 8)
    indices = [i for i in range(9) if not fixed_cells[row][i]]
    if len(indices) >= 2:
        i1, i2 = random.sample(indices, 2)
        individual[row][i1], individual[row][i2] = (
            individual[row][i2],
            individual[row][i1],
        )

def crossover(parent1, parent2):
    child = []
    for i in range(9):
        if random.random() < 0.5:
            child.append(copy.deepcopy(parent1[i]))
        else:
            child.append(copy.deepcopy(parent2[i]))
    return child

def genetic_algorithm(
    puzzle,
    fixed_cells,
    population_size=2500,
    generations=15000,
    max_stagnation=50,
    mutation_chance=0.92,
    elitism_count=600,
):
    # Initialize population with fitness values
    population = [
        (create_individual(puzzle, fixed_cells), 0) for _ in range(population_size)
    ]
    # Compute fitness for initial population
    for i in range(population_size):
        population[i] = (population[i][0], fitness(population[i][0]))

    # Sort initial population
    population.sort(key=lambda ind: ind[1])

    best_fitness = population[0][1]
    stagnation_counter = 0

    for generation in range(1, generations+1):
        # Sort population based on fitness
        population.sort(key=lambda ind: ind[1])
        current_fitness = population[0][1]

        if current_fitness == 0:
            print(f"Solution found at generation {generation}") #++++++++++++++++++++++++++++++++++++++++
            return population[0][0]

        if current_fitness < best_fitness:
            best_fitness = current_fitness
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        if stagnation_counter >= max_stagnation:
            print(
                f"No improvement for {max_stagnation} generations. Restarting population..."  #++++++++++++++++++++++++++++++++++++++++
            )
            population = [
                (create_individual(puzzle, fixed_cells), 0)
                for _ in range(population_size)
            ]
            for i in range(population_size):
                population[i] = (population[i][0], fitness(population[i][0]))
            # Sort the new population
            population.sort(key=lambda ind: ind[1])
            best_fitness = population[0][1]
            stagnation_counter = 0

        new_population = population[:elitism_count]  # Elitism

        while len(new_population) < population_size:
            parents = random.sample(population[:elitism_count], 2)
            child = crossover(parents[0][0], parents[1][0])
            if random.random() < mutation_chance:
                mutate(child, fixed_cells)
            child_fitness = fitness(child)
            new_population.append((child, child_fitness))

        population = new_population

        # Print current generation
        print(f"Generation {generation}, Best fitness: {population[0][1]}")  #++++++++++++++++++++++++++++++++++++++++

    print("No solution found.")
    return population[0][0]

def main():
    # Чтение из файла закомментировано
    puzzle = read_puzzle("assignment 2/input.txt")
    
    # Чтение из консоли
    # puzzle = read_puzzle_console()
    
    fixed_cells = [[cell != 0 for cell in row] for row in puzzle]

    solution = genetic_algorithm(
        puzzle,
        fixed_cells,
        population_size=2500,
        generations=15000,
        max_stagnation=50,
        mutation_chance=0.92,
        elitism_count=600,
    )
    
    # Запись в файл закомментировано
    write_solution(solution, "output.txt") 
    
    # Вывод решения в консоль
    # print("\nРешение судоку:")
    # write_solution_console(solution) #
    # Опционально: печать судоку с подчеркиваниями для пустых ячеек
    # print_puzzle(solution)

if __name__ == "__main__":
    main()