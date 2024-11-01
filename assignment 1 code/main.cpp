#include <iostream>
#include <sstream>
#include <vector>
#include <queue>
#include <set>
#include <tuple>
#include <string>
#include <utility>
#include <cmath>

using namespace std;

class Astar {
public:
    // Constructor to initialize the A* agent with the Keymaker's position
    Astar(pair<int, int> keymakerPos) {
        keymakerPosition = keymakerPos;
        backdoorKeyPosition = {-1, -1}; // Initial backdoor position set to invalid
        currentPosition = {0, 0};       // Agent starts at (0,0)
        moveCount = 0;                  // Counter for moves taken
    }

    // Method to decide the next move or action for the agent
    string decideMove() {
        processObservations();  // Process the surrounding observations
        pair<int, int> nextStep = performAStarSearch(keymakerPosition);  // Calculate next step using A*

        // Check if agent has reached the Keymaker's position
        if (currentPosition == keymakerPosition) {
            int shortestPathLength = computeShortestDistance();  // Compute shortest distance to goal
            return "e " + to_string(shortestPathLength);         // End the game if reached
        }

        // If destination is unreachable
        if (nextStep.first == -1 && nextStep.second == -1) {
            return "e -1"; // Indicate that the path is unsolvable
        }

        // Update agent's current position and increment move count
        currentPosition = nextStep;
        moveCount++;
        return "m " + to_string(nextStep.second) + " " + to_string(nextStep.first);
    }

private:
    pair<int, int> keymakerPosition;      // Position of the Keymaker
    pair<int, int> backdoorKeyPosition;   // Position of the Backdoor Key if found
    set<pair<int, int>> dangerCells;      // Set of cells containing dangerous entities
    pair<int, int> currentPosition;       // Current position of the agent
    int moveCount;                        // Total number of moves taken by the agent

    // Reads observations of surrounding environment, marking danger and backdoor key positions
    void processObservations() {
        int numObservations;
        cin >> numObservations;
        cin.ignore();
        for (int i = 0; i < numObservations; ++i) {
            string line;
            getline(cin, line);
            if (line.empty()) {
                --i;  // Re-read if line is empty
                continue;
            }
            istringstream iss(line);
            int y, x;
            string obj;
            if (iss >> y >> x >> obj) {
                if (obj == "P" || obj == "A" || obj == "S") {
                    dangerCells.insert({x, y});  // Add danger cell coordinates
                }
                if (obj == "B") {
                    backdoorKeyPosition = {x, y};  // Store backdoor key position
                }
            }
        }
    }

    // Calculate Manhattan distance between two points, used as a heuristic in A*
    int calculateManhattanDistance(pair<int, int> start, pair<int, int> end) {
        return abs(start.first - end.first) + abs(start.second - end.second);
    }

    // Generates valid moves that avoid danger cells and stay within grid bounds
    vector<pair<int, int>> generateValidMoves(pair<int, int> position, set<pair<int, int>>& visitedCells) {
        vector<pair<int, int>> possibleMoves;
        vector<pair<int, int>> directions = {{-1,0}, {1,0}, {0,-1}, {0,1}};  // Four possible move directions
        for (auto dir : directions) {
            int newX = position.first + dir.first;
            int newY = position.second + dir.second;
            pair<int, int> newPosition = {newX, newY};

            // Skip if the cell is dangerous, out of bounds, or already visited
            if (dangerCells.find(newPosition) != dangerCells.end() ||
                newX < 0 || newX > 8 || newY < 0 || newY > 8 ||
                visitedCells.find(newPosition) != visitedCells.end()) {
                continue;
            }
            possibleMoves.push_back(newPosition);
        }
        return possibleMoves;
    }

    // Implements the A* search algorithm to find the shortest path to the destination
    pair<int, int> performAStarSearch(pair<int, int> destination) {
        set<pair<int, int>> visitedCells; // Track visited cells to avoid loops
        if (currentPosition == destination) {
            return {-1, -1};  // Destination already reached
        }

        // Define a custom tuple type and comparison function for the priority queue
        typedef tuple<int, int, int, pair<int, int>, vector<pair<int, int>>> SearchNode;
        auto compareNodes = [](const SearchNode& a, const SearchNode& b) {
            return get<0>(a) > get<0>(b);  // Compare based on f-score
        };

        // Priority queue for A* nodes, sorted by f-score (lowest to highest)
        priority_queue<SearchNode, vector<SearchNode>, decltype(compareNodes)> openSet(compareNodes);

        // Calculate initial heuristic and add the starting node to the queue
        int heuristic = calculateManhattanDistance(currentPosition, destination);
        openSet.push(make_tuple(heuristic, 0, heuristic, currentPosition, vector<pair<int, int>>()));

        // Process nodes in openSet until the destination is reached or no paths remain
        while (!openSet.empty()) {
            SearchNode node = openSet.top();
            openSet.pop();
            int fScore = get<0>(node);
            int gScore = get<1>(node);
            int hScore = get<2>(node);
            pair<int, int> pos = get<3>(node);
            vector<pair<int, int>> path = get<4>(node);

            // Skip if node has been visited
            if (visitedCells.find(pos) != visitedCells.end()) {
                continue;
            }
            visitedCells.insert(pos);

            // If destination reached, return the first step in the path
            if (pos == destination) {
                if (!path.empty()) {
                    return path[0];
                } else {
                    return pos;
                }
            }

            // Generate valid moves and add them to the priority queue with updated scores
            vector<pair<int, int>> moves = generateValidMoves(pos, visitedCells);
            for (auto move : moves) {
                int newGScore = gScore + 1;
                int newHScore = calculateManhattanDistance(move, destination);
                int newFScore = newGScore + newHScore;
                vector<pair<int, int>> newPath = path;
                newPath.push_back(move);
                openSet.push(make_tuple(newFScore, newGScore, newHScore, move, newPath));
            }
        }
        return {-1, -1};  // Return invalid move if path to destination is not found
    }

    // Compute the shortest distance to Keymaker using BFS
    int computeShortestDistance() {
        queue<pair<int, pair<int, int>>> nodeQueue;
        set<pair<int, int>> visitedCells;
        nodeQueue.push({0, {0, 0}});  // Start BFS from initial position (0,0)

        while (!nodeQueue.empty()) {
            auto frontNode = nodeQueue.front();
            nodeQueue.pop();
            int currentLength = frontNode.first;
            pair<int, int> pos = frontNode.second;

            // Skip if cell is already visited
            if (visitedCells.find(pos) != visitedCells.end()) {
                continue;
            }
            visitedCells.insert(pos);

            // Return path length if Keymaker is reached
            if (pos == keymakerPosition) {
                return currentLength;
            }

            // Add neighboring cells to the queue
            vector<pair<int, int>> moves = generateValidMoves(pos, visitedCells);
            for (auto move : moves) {
                nodeQueue.push({currentLength + 1, move});
            }
        }
        return -1;  // Return -1 if no path to Keymaker exists
    }
};

int main() {
    // Read the perception variant (not used in this implementation)
    string variantLine;
    getline(cin, variantLine);
    int variant = stoi(variantLine);

    // Read Keymaker's position from input
    string keymakerInput;
    getline(cin, keymakerInput);
    istringstream iss(keymakerInput);
    int keymakerY, keymakerX;
    iss >> keymakerY >> keymakerX;

    // Initialize the A* agent with the Keymaker's position
    Astar agent({keymakerX, keymakerY});

    // Begin with an initial move at (0,0) and print the command
    cout << "m 0 0" << endl;
    cout.flush();

    // Continuously decide moves and read observations until agent ends
    while (true) {
        string action = agent.decideMove();
        cout << action << endl;
        cout.flush();

        // Exit if no action or end command is received
        if (action.empty() || action[0] == 'e') {
            break;
        }
    }
    return 0;
}
