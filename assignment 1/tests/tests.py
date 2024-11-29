import subprocess
import random
import time
import numpy as np
from collections import deque
import json
import os

# Константы
GRID_SIZE = 9
NUM_TESTS = 1000
CPLUSPLUS_PROGRAMS = {
    'astar': './astar',  # Путь к исполняемому файлу A*
    'backtracking': './b'  # Путь к исполняемому файлу Backtracking
}

# Проверка на валидность ячейки
def is_valid(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

# Добавление зон восприятия вокруг Sentinel
def add_sentinel_perception(grid, sx, sy):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] 
    for dx, dy in directions:
        nx, ny = sx + dx, sy + dy
        if is_valid(nx, ny) and grid[ny][nx] == '.':
            grid[ny][nx] = 'P'

# Добавление зон восприятия вокруг Agent Smith
def add_agent_perception(grid, ax, ay):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)] 
    for dx, dy in directions:
        nx, ny = ax + dx, ay + dy
        if is_valid(nx, ny) and grid[ny][nx] == '.':
            grid[ny][nx] = 'P'

# Генерация случайной карты
def generate_random_map():
    grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Установка Sentinel и его восприятия
    if random.choice([True, False]):  # 50% шанс появления Sentinel
        while True:
            sx, sy = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[sy][sx] == '.':
                grid[sy][sx] = 'S'
                add_sentinel_perception(grid, sx, sy)
                break
    
    # Установка Agent Smith и его восприятия (до 3 агентов)
    num_agents = random.randint(0, 3)
    for _ in range(num_agents):
        while True:
            ax, ay = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if grid[ay][ax] == '.':
                grid[ay][ax] = 'A'
                add_agent_perception(grid, ax, ay)
                break

    # Установка Backdoor Key на свободную клетку
    while True:
        bx, by = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if grid[by][bx] == '.':
            grid[by][bx] = 'B'
            break

    while True:
        kx, ky = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if grid[ky][kx] == '.':
            grid[ky][kx] = 'K'
            break

    return grid, (0, 0), (kx, ky)

def bfs(grid, start, goal):
    queue = deque()
    queue.append((start[0], start[1], 0))  
    visited = set()
    visited.add((start[0], start[1]))
    
    while queue:
        x, y, dist = queue.popleft()
        if (x, y) == goal:
            return dist
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and (nx, ny) not in visited:
                if grid[ny][nx] in ['.', 'B', 'K']:  
                    queue.append((nx, ny, dist + 1))
                    visited.add((nx, ny))
    return -1 

def map_to_input(perception_variant, keymaker_pos, grid):
    input_data = f"{perception_variant}\n{keymaker_pos[0]} {keymaker_pos[1]}\n"
    for row in grid:
        input_data += ''.join(row) + '\n'
    return input_data
def run_cpp_program(program, perception_variant, grid, start_pos, keymaker_pos, expected_path_length=None, timeout=20):  # Увеличиваем тайм-аут до 20 секунд
    input_data = map_to_input(perception_variant, keymaker_pos, grid)
    try:
        process = subprocess.Popen(
            [CPLUSPLUS_PROGRAMS[program]],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Передача данных
        process.stdin.write(input_data)
        process.stdin.flush()

        # Счетчик времени выполнения
        start_time = time.time()

        try:
            # Чтение всех выходных данных с тайм-аутом
            output, errors = process.communicate(timeout=timeout)
            exec_time = time.time() - start_time

            # Парсинг результата
            success, path_length = False, -1
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("e"):
                    parts = line.split()
                    if len(parts) == 2 and parts[1].isdigit():
                        path_length = int(parts[1])
                        # Проверка: путь найден и совпадает с ожидаемым, если он задан
                        if expected_path_length is not None:
                            success = (path_length == expected_path_length)
                        else:
                            success = (path_length != -1)
                        # Логирование несоответствий
                        if expected_path_length is not None and path_length != expected_path_length:
                            print(f"Discrepancy detected: Expected path length {expected_path_length}, but got {path_length}")
                        else:
                            print(f"Path length matched expected: {path_length}")
                    break

            process.terminate()
            return exec_time, success, path_length

        except subprocess.TimeoutExpired:
            process.kill()
            exec_time = time.time() - start_time
            print("Process timed out.")
            return exec_time, False, -1

    except Exception as e:
        print(f"Error: {e}")
        return None, False, -1

# Функция для тестирования и сбора данных с сохранением и загрузкой тестов
def run_tests(algorithm):
    times, successes, path_lengths = [], [], []
    tests = []

    # Проверка существования файла с тестами
    if os.path.exists('tests.txt'):
        with open('tests.txt', 'r') as f:
            tests = json.load(f)
        print("Loaded tests from tests.txt")
    else:
        # Генерация 1000 тестов
        for _ in range(NUM_TESTS):
            grid, start_pos, keymaker_pos = generate_random_map()
            perception_variant = random.choice([1, 2])
            expected_path_length = bfs(grid, start_pos, keymaker_pos)
            tests.append({
                'perception_variant': perception_variant,
                'grid': grid,
                'keymaker_pos': keymaker_pos,
                'expected_path_length': expected_path_length
            })
        # Сохранение тестов в файл
        with open('tests.txt', 'w') as f:
            json.dump(tests, f)
        print("Generated and saved tests to tests.txt")

    # Демонстрация одного теста
    example_test = tests[0]
    print("Example Test Case:")
    for row in example_test['grid']:
        print("".join(row))
    print(f"Keymaker Position: {example_test['keymaker_pos']}")
    print(f"Perception Variant: {example_test['perception_variant']}")
    
    exec_time, success, path_length = run_cpp_program(
        algorithm, 
        example_test['perception_variant'], 
        example_test['grid'], 
        (0, 0), 
        example_test['keymaker_pos'], 
        example_test['expected_path_length']
    )
    exec_time = exec_time if exec_time is not None else 0.0
    print(f"Execution Time: {exec_time:.4f} seconds")
    print(f"Success: {success}")
    print(f"Path Length: {path_length if path_length != -1 else 'Unreachable'}\n")

    # Запуск всех тестов
    for idx, test in enumerate(tests[1:], start=2):
        perception_variant = test['perception_variant']
        grid = test['grid']
        keymaker_pos = test['keymaker_pos']
        expected_path_length = test['expected_path_length']
        
        exec_time, success, path_length = run_cpp_program(
            algorithm, 
            perception_variant, 
            grid, 
            (0, 0), 
            keymaker_pos, 
            expected_path_length
        )
        if exec_time is not None:
            times.append(exec_time)
            successes.append(success)
            if success:
                path_lengths.append(path_length)
        
        if idx % 100 == 0:
            print(f"Completed {idx} / {NUM_TESTS} tests.")

    return times, successes, path_lengths

# Вычисление статы
def calculate_statistics(times, successes, path_lengths):
    stats_dict = {
        'Mean Execution Time': np.mean(times) if times else None,
        'Median Execution Time': np.median(times) if times else None,
        'Execution Time Std Dev': np.std(times) if times else None,
        'Success Rate': (sum(successes) / len(successes) * 100) if successes else 0,
        'Failure Rate': (100 - (sum(successes) / len(successes) * 100)) if successes else 100
    }
    if path_lengths:
        stats_dict['Mean Path Length'] = np.mean(path_lengths)
        stats_dict['Median Path Length'] = np.median(path_lengths)
        stats_dict['Path Length Std Dev'] = np.std(path_lengths)
    else:
        stats_dict['Mean Path Length'] = None
        stats_dict['Median Path Length'] = None
        stats_dict['Path Length Std Dev'] = None

    return stats_dict

# Основная функция
def main():
    algorithm = input("Enter algorithm ('astar' or 'backtracking'): ").strip()

    if algorithm not in CPLUSPLUS_PROGRAMS:
        print("Invalid algorithm selected.")
        return

    times, successes, path_lengths = run_tests(algorithm)
    
    # Вывод статистики
    print(f"\n{algorithm.upper()} Algorithm Statistics:")
    stats_result = calculate_statistics(times, successes, path_lengths)
    for key, value in stats_result.items():
        if isinstance(value, float):
            print(f"{key}: {value:.6f}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
