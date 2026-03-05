# Campus City Emergency Supply Distribution

**24MAT382 - Computational Optimization and Applications**

## Project Summary

[cite_start]This micro-project implements a computational solution to optimize the emergency supply distribution network for Campus City Logistics[cite: 1, 5]. [cite_start]The objective is to identify a real-time problem, formulate it mathematically, and implement a computational solution using Python[cite: 7]. The model utilizes a Mixed-Integer Linear Programming (MILP) formulation to select exactly two warehouse locations to supply six campus facilities. It minimizes the total annual cost—including amortized construction, daily operations, and transportation—while strictly satisfying facility demands, respecting warehouse capacities, and operating within a $1,500,000 annual budget.

## Repository Structure

[cite_start]The repository contains the following folders and files[cite: 19]:

- [cite_start]`/src`: Contains the complete executable Python source code (`main.py` and/or `main.ipynb`) containing the MILP formulation.
- [cite_start]`/data`: Contains the CSV datasets (`facilities.csv`, `warehouses.csv`, `transportation_costs.csv`) used for the problem[cite: 21].
- `requirements.txt`: Lists the Python library dependencies required to execute the model.
- [cite_start]`README.md`: A documentation file explaining how to run the code, required dependencies, and a brief problem summary[cite: 22, 23].
- [cite_start]`Report.pdf`: The final technical report detailing the problem statement, mathematical formulation, methodology, and results analysis[cite: 24, 25, 26, 27, 30, 31].

## Dependencies Required

This project requires Python. The computational implementation relies on specific libraries to read the datasets and solve the mathematical model.

All required packages are listed in `requirements.txt`:

- `pulp`
- `pandas`

To install all dependencies in your environment, run:

```bash
pip install -r requirements.txt
```
