#include <iostream>
#include <vector>
#include <queue>
#include <deque>
#include <set>
#include <map>
#include <string>
#include <sstream>
#include <algorithm>

using namespace std;

class Backtracking {
public:
    // Current position of the agent
    pair<int, int> curr_place;

    // Set of dangerous cells containing enemies or hazards
    set<pair<int, int>> dead_cells;

    // Target position of the Keymaker
    pair<int, int> trogaem_deda;

    // Agent's vision range
    int vision_range;

    // Path that the agent is following
    vector<pair<int, int>> path_trace;

    // Current step index in path_trace
    int n_step;

    // Total number of actions taken
    int total_actions;

    // Flags indicating if the Keymaker or Backdoor Key has been found
    bool key_found;
    bool backdoor_key_found;

    // Set of visited cells for tracking purposes
    set<pair<int, int>> vis;

    // Constructor to initialize the agent with the Keymaker's position and vision range
    Backtracking(pair<int, int> trogaem_deda, int vision_range) {
        curr_place = make_pair(0, 0); // Starting at (0,0)
        this->trogaem_deda = trogaem_deda;
        this->vision_range = vision_range;
        n_step = -1;
        total_actions = 0;
        key_found = false;
        backdoor_key_found = false;
    }

    // Checks if a cell is within bounds and not in a danger zone
    bool is_legal(int x, int y) {
        if (x < 0 || y < 0 || x > 8 || y > 8)
            return false;
        if (dead_cells.find(make_pair(x, y)) != dead_cells.end())
            return false;
        return true;
    }

    // Generates legal moves that do not enter dangerous cells
    vector<pair<int, int>> not_dang_steps(pair<int, int> position) {
        int x = position.first;
        int y = position.second;
        vector<pair<int, int>> moves = {
                make_pair(x - 1, y),
                make_pair(x + 1, y),
                make_pair(x, y - 1),
                make_pair(x, y + 1)
        };
        vector<pair<int, int>> result;
        for (auto move : moves) {
            if (is_legal(move.first, move.second)) {
                result.push_back(move);
            }
        }
        return result;
    }

    // Stores observations from the environment and updates dangerous zones or key position
    void st_ob(vector<vector<string>>& ob) {
        bool keymaker_found_in_obs = false;
        for (auto& line : ob) {
            if (line.size() >= 3) {
                int x = stoi(line[0]);
                int y = stoi(line[1]);
                string obj = line[2];
                if (obj == "P" || obj == "A" || obj == "S") {
                    dead_cells.insert(make_pair(x, y)); // Mark cell as dangerous
                }
                if (obj == "K") {
                    // Update Keymaker's position if changed
                    if (trogaem_deda != make_pair(x, y)) {
                        trogaem_deda = make_pair(x, y);
                        n_step = -1; // Reset path for recalculation
                    }
                    key_found = true;
                    keymaker_found_in_obs = true;
                }
            }
        }

    }

    // Uses BFS to find the shortest path from start to target, avoiding danger zones
    void shortest_path(pair<int, int> start, pair<int, int> target) {
        set<pair<int, int>> vis_local; // Local set of visited nodes for BFS
        deque<pair<pair<int, int>, vector<pair<int, int>>>> waiting;
        waiting.push_back(make_pair(start, vector<pair<int, int>>())); // Queue initialized with start position
        vis_local.insert(start);

        while (!waiting.empty()) {
            auto front = waiting.front();
            waiting.pop_front();
            pair<int, int> position = front.first;
            vector<pair<int, int>> path_trace = front.second;

            if (position == target) {
                path_trace.push_back(position);
                this->path_trace = path_trace;
                n_step = 1; // Path found; start tracking steps
                return;
            }
            for (auto move : not_dang_steps(position)) {
                if (vis_local.find(move) == vis_local.end()) {
                    vis_local.insert(move);
                    vector<pair<int, int>> new_path = path_trace;
                    new_path.push_back(position);
                    waiting.push_back(make_pair(move, new_path));
                }
            }
        }
        n_step = -1; // Path not found
    }

    // Finds the shortest distance from the start to the Keymaker, avoiding dangerous zones
    int opt_path() {
        deque<pair<int, pair<int, int>>> waiting;
        waiting.push_back(make_pair(0, make_pair(0, 0)));
        set<pair<int, int>> vis_local;
        vis_local.insert(make_pair(0, 0));

        while (!waiting.empty()) {
            auto front = waiting.front();
            waiting.pop_front();
            int cur_len = front.first;
            pair<int, int> pos = front.second;

            if (pos == trogaem_deda) {
                return cur_len; // Return shortest distance to Keymaker
            }
            for (auto move : not_dang_steps(pos)) {
                if (vis_local.find(move) == vis_local.end()) {
                    vis_local.insert(move);
                    waiting.push_back(make_pair(cur_len + 1, move));
                }
            }
        }
        return -1; // Path to Keymaker not found
    }

    // Decides the next move based on observations and updates path accordingly
    string step(vector<vector<string>>& ob) {
        st_ob(ob); // Process observations


        if (n_step != -1) {
            // If we have reached the end of the path, output the shortest distance
            if (n_step >= path_trace.size()) {

                int shortest_distance = opt_path();
                return "e " + to_string(shortest_distance);
            }
            pair<int, int> next_position = path_trace[n_step];
            // If the next position is dangerous, reset path
            if (dead_cells.find(next_position) != dead_cells.end()) {
                n_step = -1;
            }
        }


        // Recalculate path if it is invalid or dangerous
        if (n_step == -1) {
            shortest_path(curr_place, trogaem_deda);
            if (n_step == -1) {
                return "e -1"; // Path not found
            }
        }


        // Move to the next position in path
        pair<int, int> next_position = path_trace[n_step];
        if (dead_cells.find(next_position) != dead_cells.end()) {
            n_step = -1; // Path invalid, recompute
            return step(ob);
        }
        curr_place = next_position;
        n_step += 1;
        return "m " + to_string(curr_place.first) + " " + to_string(curr_place.second);
    }
};
int main() {
    // Read the perception variant for the agent
    int perception_variant;
    cin >> perception_variant;

    // Read the coordinates of the Keymaker
    int keymaker_x, keymaker_y;
    cin >> keymaker_x >> keymaker_y;

    // Initialize the Backtracking with the Keymaker's position and perception variant
    Backtracking agent(make_pair(keymaker_x, keymaker_y), perception_variant);

    // First move: Agent starts at (0,0) and takes an initial safe step
    cout << "m 0 0" << endl;
    cout.flush();

    // Variable to store the number of observed dangers and positions around the agent
    string obs_count_line;
    getline(cin, obs_count_line);

    // Main loop: Continue receiving observations and deciding moves until the agent reaches the Keymaker
    while (true) {
        if (!obs_count_line.empty()) {
            int obs_count = stoi(obs_count_line);

            // Read the details of observed dangers for the agent
            vector<vector<string>> ob;
            for (int i = 0; i < obs_count; ++i) {
                string line;
                getline(cin, line);
                istringstream iss(line);
                vector<string> tokens;
                string token;
                while (iss >> token) {
                    tokens.push_back(token);
                }
                ob.push_back(tokens);
            }

            // Calculate the agent's next action based on the observations
            string action = agent.step(ob);
            cout << action << endl;
            cout.flush();

            // Exit loop if the action is an end command (indicating completion or failure)
            if (action[0] == 'e') break;
        }

        // Read the next line to update the observation count or break if input ends
        if (!getline(cin, obs_count_line)) break;
    }
    return 0;
}
