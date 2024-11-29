using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace sudokuGenetivAlgoritm
{
    class Program
    {
        // Random number generator used throughout the genetic algorithm
        static Random random = new Random();

        /// <summary>
        /// Reads a Sudoku puzzle from the console input.
        /// Expects 9 lines of input, each containing 9 elements separated by spaces.
        /// Givens can be single-digit numbers (1-9), hyphens '-', zeros '0', or underscores '_'.
        /// Hyphens, zeros, and underscores represent empty cells.
        /// </summary>
        /// <returns>A 9x9 integer array representing the Sudoku puzzle.</returns>
        static int[][] ReadPazzCons()
        {
            int[][] pazz = new int[9][];
            for (int i = 0; i < 9; i++)
            {
                while (true)
                {
                    try
                    {
                        // Read a line from the console
                        string input = Console.ReadLine();
                        if (input == null)
                            throw new ArgumentNullException("Input cannot be null");

                        // Split the input line into tokens separated by spaces
                        string[] tokens = input.Trim().Split(' ');
                        if (tokens.Length != 9)
                            throw new ArgumentException("Each line must contain exactly 9 elements");

                        pazz[i] = new int[9];
                        for (int j = 0; j < 9; j++)
                        {
                            // Check for empty cell indicators
                            if (tokens[j] == "-" || tokens[j] == "0" || tokens[j] == "_")
                            {
                                pazz[i][j] = 0; // Represent empty cells with 0
                            }
                            else
                            {
                                // Attempt to parse the token as an integer
                                if (!int.TryParse(tokens[j], out int num))
                                    throw new ArgumentException("Invalid number format");

                                // Ensure the number is within the valid range
                                if (num < 1 || num > 9)
                                    throw new ArgumentException("Numbers must be between 1 and 9");

                                pazz[i][j] = num; // Assign the parsed number to the puzzle
                            }
                        }
                        break; // Exit the loop if the line is successfully parsed
                    }
                    catch (Exception ex)
                    {
                        // Inform the user of any input errors and prompt to re-enter the line
                        Console.WriteLine($"Error: {ex.Message}. Enter the line again");
                    }
                }
            }
            return pazz; // Return the fully read Sudoku puzzle
        }

        /// <summary>
        /// Writes the Sudoku solution to the console.
        /// Each row is printed on a new line with numbers separated by spaces.
        /// </summary>
        /// <param name="solution">The solved Sudoku puzzle as a 9x9 integer array.</param>
        static void WriteSolutionConsole(int[][] solution)
        {
            foreach (var row in solution)
            {
                // Convert each number in the row to a string and join them with spaces
                Console.WriteLine(string.Join(" ", row.Select(val => val.ToString())));
            }
        }

        /// <summary>
        /// Calculates the fitness score of a Sudoku individual.
        /// The fitness score represents the number of rule violations:
        /// - Duplicate numbers in rows
        /// - Duplicate numbers in columns
        /// - Duplicate numbers in 3x3 subgrids
        /// A lower score is better, with a score of 0 indicating a valid solution.
        /// </summary>
        /// <param name="individual">A 9x9 integer array representing a Sudoku solution.</param>
        /// <returns>The fitness score as an integer.</returns>
        static int Fitness(int[][] individual)
        {
            int score = 0; // Initialize fitness score
            bool[] seen = new bool[10]; // Array to track seen numbers (1-9)

            // Evaluate row fitness
            for (int i = 0; i < 9; i++)
            {
                Array.Clear(seen, 1, 9); // Reset seen array for the new row
                for (int j = 0; j < 9; j++)
                {
                    int val = individual[i][j];
                    if (seen[val])
                        score++; // Increment score for duplicate in row
                    else
                        seen[val] = true; // Mark number as seen
                }
            }

            // Evaluate column fitness
            for (int j = 0; j < 9; j++)
            {
                Array.Clear(seen, 1, 9); // Reset seen array for the new column
                for (int i = 0; i < 9; i++)
                {
                    int val = individual[i][j];
                    if (seen[val])
                        score++; // Increment score for duplicate in column
                    else
                        seen[val] = true; // Mark number as seen
                }
            }

            // Evaluate subgrid fitness
            for (int blockRow = 0; blockRow < 3; blockRow++)
            {
                for (int blockCol = 0; blockCol < 3; blockCol++)
                {
                    Array.Clear(seen, 1, 9); // Reset seen array for the new subgrid
                    for (int i = 0; i < 3; i++)
                    {
                        for (int j = 0; j < 3; j++)
                        {
                            int val = individual[blockRow * 3 + i][blockCol * 3 + j];
                            if (seen[val])
                                score++; // Increment score for duplicate in subgrid
                            else
                                seen[val] = true; // Mark number as seen
                        }
                    }
                }
            }

            return score; // Return the total fitness score
        }

        /// <summary>
        /// Creates an individual Sudoku solution based on the initial puzzle and fixed cells.
        /// Fixed cells (givens) are preserved, and empty cells are filled with random available numbers.
        /// </summary>
        /// <param name="pazz">The initial Sudoku puzzle as a 9x9 integer array.</param>
        /// <param name="fixedCells">A 9x9 boolean array indicating which cells are fixed.</param>
        /// <returns>A new individual Sudoku solution as a 9x9 integer array.</returns>
        static int[][] CreateIndividual(int[][] pazz, bool[][] fixedCells)
        {
            int[][] individual = new int[9][];
            for (int i = 0; i < 9; i++)
            {
                individual[i] = new int[9];
                int[] availableNumbers = new int[9]; // Array to hold available numbers for the row
                int count = 0;

                // Determine which numbers are not already present in the row
                for (int n = 1; n <= 9; n++)
                {
                    bool found = false;
                    for (int j = 0; j < 9; j++)
                    {
                        if (pazz[i][j] == n)
                        {
                            found = true;
                            break;
                        }
                    }
                    if (!found)
                    {
                        availableNumbers[count++] = n; // Add available number to the list
                    }
                }

                // Shuffle the available numbers to introduce randomness
                ShuffleArray(availableNumbers, count);

                int idx = 0; // Index to track the next available number
                for (int j = 0; j < 9; j++)
                {
                    if (fixedCells[i][j])
                    {
                        individual[i][j] = pazz[i][j]; // Preserve fixed cell value
                    }
                    else
                    {
                        if (idx < count)
                        {
                            individual[i][j] = availableNumbers[idx++]; // Assign available number
                        }
                        else
                        {
                            individual[i][j] = random.Next(1, 10); // Assign a random number if no available numbers left
                        }
                    }
                }
            }
            return individual; // Return the newly created individual
        }

        /// <summary>
        /// Shuffles an array in place using the Fisher-Yates algorithm.
        /// Only the first 'count' elements of the array are considered for shuffling.
        /// </summary>
        /// <param name="array">The array to shuffle.</param>
        /// <param name="count">The number of elements to shuffle.</param>
        static void ShuffleArray(int[] array, int count)
        {
            for (int i = count - 1; i > 0; i--)
            {
                int j = random.Next(i + 1); // Generate a random index
                // Swap the elements at indices i and j
                int temp = array[i];
                array[i] = array[j];
                array[j] = temp;
            }
        }

        /// <summary>
        /// Mutates an individual by swapping two non-fixed cells within a randomly selected row.
        /// Mutation introduces diversity into the population by altering individuals.
        /// </summary>
        /// <param name="individual">The Sudoku individual to mutate.</param>
        /// <param name="fixedCells">A 9x9 boolean array indicating which cells are fixed.</param>
        static void Mutate(int[][] individual, bool[][] fixedCells)
        {
            int row = random.Next(9); // Select a random row
            int[] mutableIndices = new int[9]; // Array to hold indices of mutable (non-fixed) cells
            int count = 0;

            // Identify all mutable cells in the selected row
            for (int i = 0; i < 9; i++)
            {
                if (!fixedCells[row][i])
                {
                    mutableIndices[count++] = i;
                }
            }

            // Ensure there are at least two mutable cells to perform a swap
            if (count >= 2)
            {
                // Select two distinct random indices to swap
                int idx1 = random.Next(count);
                int idx2 = random.Next(count - 1);
                if (idx2 >= idx1)
                    idx2++;
                int col1 = mutableIndices[idx1];
                int col2 = mutableIndices[idx2];

                // Perform the swap of values in the selected cells
                int temp = individual[row][col1];
                individual[row][col1] = individual[row][col2];
                individual[row][col2] = temp;
            }
        }

        /// <summary>
        /// Performs crossover between two parent individuals to produce a child individual.
        /// The crossover point is randomly selected, and rows before the crossover point are taken from parent1,
        /// while rows from the crossover point onward are taken from parent2.
        /// </summary>
        /// <param name="parent1">The first parent Sudoku individual.</param>
        /// <param name="parent2">The second parent Sudoku individual.</param>
        /// <returns>A new child Sudoku individual resulting from the crossover.</returns>
        static int[][] Crossover(int[][] parent1, int[][] parent2)
        {
            int[][] child = new int[9][];
            int crossoverPoint = random.Next(1, 9); // Randomly select a crossover point between 1 and 8
            for (int i = 0; i < 9; i++)
            {
                child[i] = new int[9];
                if (i < crossoverPoint)
                {
                    Array.Copy(parent1[i], child[i], 9); // Copy row from parent1
                }
                else
                {
                    Array.Copy(parent2[i], child[i], 9); // Copy row from parent2
                }
            }
            return child; // Return the resulting child individual
        }

        /// <summary>
        /// Executes the Genetic Algorithm to solve the Sudoku puzzle.
        /// The algorithm evolves a population of Sudoku solutions over multiple generations
        /// to minimize the fitness score, ultimately finding a valid solution.
        /// </summary>
        /// <param name="pazz">The initial Sudoku puzzle as a 9x9 integer array.</param>
        /// <param name="fixedCells">A 9x9 boolean array indicating which cells are fixed.</param>
        /// <param name="populationSize">The number of individuals in the population.</param>
        /// <param name="generations">The maximum number of generations to run the algorithm.</param>
        /// <param name="maxStagnat">The maximum number of generations allowed without improvement before restarting.</param>
        /// <param name="mutatiuons">The mutation rate (probability of mutation).</param>
        /// <param name="elitismCount">The number of top individuals to carry over unchanged to the next generation.</param>
        /// <returns>The best Sudoku solution found as a 9x9 integer array.</returns>
        static int[][] GeneticAlgorithm(
            int[][] pazz,
            bool[][] fixedCells,
            int populationSize = 2500,
            int generations = 15000,
            int maxStagnat = 50,
            double mutatiuons = 0.92,
            int elitismCount = 500)
        {
            // Initialize the population with random individuals and calculate their fitness
            List<(int[][] Individual, int Fitness)> population = new List<(int[][], int)>(populationSize);
            for (int i = 0; i < populationSize; i++)
            {
                int[][] individual = CreateIndividual(pazz, fixedCells); // Create a new individual
                int fit = Fitness(individual); // Calculate its fitness
                population.Add((individual, fit)); // Add to the population
            }

            // Sort the initial population based on fitness (ascending order)
            population.Sort((a, b) => a.Fitness.CompareTo(b.Fitness));

            int bestFitness = population[0].Fitness; // Best fitness in the population
            int stagnationCounter = 0; // Counter to track stagnation

            // Iterate through the specified number of generations
            for (int generation = 1; generation <= generations; generation++)
            {
                // Sort the population based on fitness
                population.Sort((a, b) => a.Fitness.CompareTo(b.Fitness));
                int currentFitness = population[0].Fitness; // Best fitness in the current generation

                if (currentFitness == 0)
                {
                    // If a perfect solution is found, return it immediately
                    return population[0].Individual;
                }

                if (currentFitness < bestFitness)
                {
                    // If there's an improvement in fitness, update bestFitness and reset stagnation counter
                    bestFitness = currentFitness;
                    stagnationCounter = 0;
                }
                else
                {
                    // If no improvement, increment the stagnation counter
                    stagnationCounter++;
                }

                if (stagnationCounter >= maxStagnat)
                {
                    // If stagnation exceeds the maximum allowed, restart the population
                    population.Clear();
                    for (int i = 0; i < populationSize; i++)
                    {
                        int[][] individual = CreateIndividual(pazz, fixedCells); // Create a new individual
                        int fit = Fitness(individual); // Calculate its fitness
                        population.Add((individual, fit)); // Add to the population
                    }
                    population.Sort((a, b) => a.Fitness.CompareTo(b.Fitness)); // Sort the new population
                    bestFitness = population[0].Fitness; // Update the best fitness
                    stagnationCounter = 0; // Reset the stagnation counter
                }

                List<(int[][] Individual, int Fitness)> newPopulation = new List<(int[][], int)>(elitismCount);
                // Apply elitism by carrying over the top-performing individuals unchanged
                for (int i = 0; i < elitismCount; i++)
                {
                    newPopulation.Add(population[i]);
                }

                // Generate the rest of the new population through crossover and mutation
                while (newPopulation.Count < populationSize)
                {
                    var parents = new List<(int[][] Individual, int Fitness)>(2);
                    // Select two parents randomly from the top elitismCount individuals
                    for (int i = 0; i < 2; i++)
                    {
                        int idx = random.Next(elitismCount);
                        parents.Add(population[idx]);
                    }

                    int[][] child = Crossover(parents[0].Individual, parents[1].Individual); // Perform crossover
                    if (random.NextDouble() < mutatiuons)
                    {
                        Mutate(child, fixedCells); // Apply mutation based on mutation rate
                    }
                    int childFitness = Fitness(child); // Calculate fitness of the child
                    newPopulation.Add((child, childFitness)); // Add child to the new population
                }

                // Parallelize the fitness evaluation for improved performance
                Parallel.ForEach(newPopulation, ind =>
                {
                    ind.Fitness = Fitness(ind.Individual);
                });

                population = newPopulation; // Replace the old population with the new one
            }

            // If no perfect solution is found within the generation limit, return the best found
            Console.WriteLine("No solution found.");
            return population.OrderBy(ind => ind.Fitness).First().Individual;
        }

        /// <summary>
        /// The main entry point of the program.
        /// It reads the Sudoku puzzle from the console, initializes fixed cells,
        /// runs the genetic algorithm to solve the puzzle, and outputs the solution.
        /// </summary>
        /// <param name="args">Command-line arguments (not used).</param>
        static void Main(string[] args)
        {
            // Read the Sudoku puzzle from the console input
            int[][] pazz = ReadPazzCons();

            // Initialize a 9x9 boolean array to mark fixed cells (givens)
            bool[][] fixedCells = new bool[9][];
            for (int i = 0; i < 9; i++)
            {
                fixedCells[i] = new bool[9];
                for (int j = 0; j < 9; j++)
                {
                    fixedCells[i][j] = pazz[i][j] != 0; // Mark cell as fixed if it's not zero
                }
            }

            // Execute the genetic algorithm with specified parameters
            int[][] solution = GeneticAlgorithm(
                pazz,
                fixedCells,
                populationSize: 2500,    // Number of individuals in each generation
                generations: 15000,      // Maximum number of generations to run
                maxStagnat: 50,           // Maximum allowed generations without improvement
                mutatiuons: 0.92,         // Mutation rate (92%)
                elitismCount: 500         // Number of top individuals to retain each generation
            );

            // Output the solved Sudoku puzzle to the console
            WriteSolutionConsole(solution);
        }
    }
}
