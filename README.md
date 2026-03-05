# Campus City Emergency Supply Distribution

**24MAT382 - Computational Optimization and Applications**

## Project Summary

This micro-project implements a computational solution to optimize the emergency supply distribution network for Campus City Logistics. The objective is to identify a real-time problem, formulate it mathematically, and implement a computational solution using Python. The model utilizes a Mixed-Integer Linear Programming (MILP) formulation to select exactly two warehouse locations to supply six campus facilities. It minimizes the total annual cost—including amortized construction, daily operations, and transportation—while strictly satisfying facility demands, respecting warehouse capacities, and operating within a $1,500,000 annual budget.

## Repository Structure

The repository contains the following folders and files:

- `/src`: Contains the executable Python source code (`main.py`) with the MILP formulation and interactive map generation.
- `/data`: Contains the CSV datasets (`facilities.csv`, `warehouses.csv`, `transportation_costs.csv`) used for the problem.
- `/scripts`: Contains utility scripts for data generation (`generate_data.py`).
- `requirements.txt`: Lists the Python library dependencies required to execute the model.
- `README.md`: This documentation file explaining how to run the code, required dependencies, and a brief problem summary.

## Dependencies Required

This project requires Python. The computational implementation relies on specific libraries to read the datasets, solve the mathematical model, and generate an interactive map.

All required packages are listed in `requirements.txt`:

- `pulp` — MILP solver interface
- `pandas` — Data ingestion and processing
- `folium` — Interactive map visualization

To install all dependencies in your environment, run:

```bash
pip install -r requirements.txt
```

## How to Run

1. Install the dependencies listed above.
2. From the **project root directory**, run:

```bash
python src/main.py
```

3. The optimization results will be printed to the terminal and an interactive map will be saved as `output/optimized_campus_map.html`.
