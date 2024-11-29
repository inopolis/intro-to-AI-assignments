import random
import copy
import matplotlib.pyplot as plt


# Sudoku puzzle generation function based on difficulty
def generate_sudoku(difficulty="easy"):
    """
    Generate a Sudoku puzzle based on difficulty level.
    difficulty: 'easy', 'medium', 'hard', 'very_hard'
    """
    base = 3
    side = base * base

    def pattern(r, c): return (base * (r % base) + r // base + c) % side
    def shuffle(s): return random.sample(s, len(s))

    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, side + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    squares = side * side
    empties = {"easy": 20, "medium": 35, "hard": 50, "very_hard": 60}.get(difficulty, 20)
    for p in random.sample(range(squares), empties):
        board[p // side][p % side] = 0

    return board


# Fitness calculation
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


# Genetic algorithm helper functions
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
    population_size=250,
    generations=500,
    max_stagnation=50,
    mutation_chance=0.9,
    elitism_count=50,
):
    population = [
        (create_individual(puzzle, fixed_cells), 0) for _ in range(population_size)
    ]
    for i in range(population_size):
        population[i] = (population[i][0], fitness(population[i][0]))

    population.sort(key=lambda ind: ind[1])
    best_fitness = population[0][1]
    stagnation_counter = 0
    fitness_history = []

    for generation in range(1, generations + 1):
        population.sort(key=lambda ind: ind[1])
        current_fitness = population[0][1]
        fitness_history.append(current_fitness)

        if current_fitness == 0:
            break

        if current_fitness < best_fitness:
            best_fitness = current_fitness
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        if stagnation_counter >= max_stagnation:
            population = [
                (create_individual(puzzle, fixed_cells), 0)
                for _ in range(population_size)
            ]
            for i in range(population_size):
                population[i] = (population[i][0], fitness(population[i][0]))
            population.sort(key=lambda ind: ind[1])
            best_fitness = population[0][1]
            stagnation_counter = 0

        new_population = population[:elitism_count]

        while len(new_population) < population_size:
            parents = random.sample(population[:elitism_count], 2)
            child = crossover(parents[0][0], parents[1][0])
            if random.random() < mutation_chance:
                mutate(child, fixed_cells)
            child_fitness = fitness(child)
            new_population.append((child, child_fitness))

        population = new_population

    return fitness_history


# Test and plotting
def run_test_sudoku():
    difficulties = ["easy", "medium", "hard", "very_hard"]
    sudoku_data = {diff: [] for diff in difficulties}

    for difficulty in difficulties:
        for _ in range(2):  # Two Sudoku puzzles per difficulty
            puzzle = generate_sudoku(difficulty)
            fixed_cells = [[cell != 0 for cell in row] for row in puzzle]
            fitness_history = genetic_algorithm(
                puzzle, fixed_cells, population_size=300, generations=500
            )
            sudoku_data[difficulty].append(fitness_history)

    return sudoku_data


def plot_fitness(sudoku_data):
    difficulty_colors = {
        "easy": "blue",
        "medium": "orange",
        "hard": "green",
        "very_hard": "red",
    }

    plt.figure(figsize=(10, 6))
    for difficulty, data in sudoku_data.items():
        avg_fitness = [sum(gen) / len(data) for gen in zip(*data)]
        plt.plot(avg_fitness, label=difficulty.capitalize(), color=difficulty_colors[difficulty])

    plt.title("avg Fitness vs generation")
    plt.xlabel("Generation")
    plt.ylabel("avg Fitness")
    plt.legend()
    plt.grid(True)
    plt.show()


# Main function
if __name__ == "__main__":
    sudoku_data = run_test_sudoku()
    plot_fitness(sudoku_data)
