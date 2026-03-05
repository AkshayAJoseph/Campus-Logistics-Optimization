import pulp
import pandas as pd

def run_optimization():
    # 1. Load Data
    # Assuming CSVs are formatted cleanly with the necessary columns
    try:
        facilities = pd.read_csv('../data/facilities.csv')
        warehouses = pd.read_csv('../data/warehouses.csv')
        transport = pd.read_csv('../data/transportation_costs.csv')
    except FileNotFoundError:
        print("Error: Ensure facilities.csv, warehouses.csv, and transportation_costs.csv are in the /data folder.")
        return

    # Extract lists of IDs
    W_IDs = warehouses['Warehouse_ID'].tolist()
    F_IDs = facilities['Facility_ID'].tolist()

    # Create dictionaries for quick lookups
    demand_dict = dict(zip(facilities['Facility_ID'], facilities['Daily_Demand']))
    cap_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Daily_Capacity']))
    construct_cost_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Construction_Cost']))
    op_cost_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Operational_Cost/Day']))

    # Create transport cost lookup (assuming columns: Warehouse_ID, Facility_ID, Cost)
    transport_dict = {}
    for _, row in transport.iterrows():
        transport_dict[(row['Warehouse_ID'], row['Facility_ID'])] = row['Cost']

    # 2. Initialize the Model
    model = pulp.LpProblem("Campus_Emergency_Supply_Distribution", pulp.LpMinimize)

    # 3. Define Decision Variables
    # y_i: 1 if warehouse is selected, 0 otherwise
    y = pulp.LpVariable.dicts("Open_Warehouse", W_IDs, cat='Binary')

    # X_ij: Annual units shipped from warehouse i to facility j
    # non-negative continuous variable
    X = pulp.LpVariable.dicts("Annual_Shipments", 
                              [(w, f) for w in W_IDs for f in F_IDs], 
                              lowBound=0, 
                              cat='Continuous')

    # 4. Objective Function: Minimize Total Annual Cost
    annual_fixed_costs = pulp.lpSum([((construct_cost_dict[w] / 10) + (365 * op_cost_dict[w])) * y[w] for w in W_IDs])
    annual_transport_costs = pulp.lpSum([transport_dict[(w, f)] * X[(w, f)] for w in W_IDs for f in F_IDs])
    
    model += annual_fixed_costs + annual_transport_costs, "Total_Annual_Cost"

    # 5. Constraints
    # Constraint A: Exactly 2 warehouses must be selected
    model += pulp.lpSum([y[w] for w in W_IDs]) == 2, "Select_Exactly_Two_Warehouses"

    # Constraint B: Each facility must receive exactly its annual demand
    for f in F_IDs:
        annual_demand = 365 * demand_dict[f]
        model += pulp.lpSum([X[(w, f)] for w in W_IDs]) == annual_demand, f"Demand_Satisfaction_{f}"

    # Constraint C: Shipments from a warehouse cannot exceed its annual capacity
    for w in W_IDs:
        annual_capacity = 365 * cap_dict[w]
        model += pulp.lpSum([X[(w, f)] for f in F_IDs]) <= annual_capacity * y[w], f"Capacity_Limit_{w}"

    # Constraint D: Total annual cost must not exceed the $1,500,000 budget
    model += (annual_fixed_costs + annual_transport_costs) <= 1500000, "Budget_Limit"

    # 6. Solve the Model
    model.solve()

    # 7. Output Results
    print(f"Optimization Status: {pulp.LpStatus[model.status]}\n")
    
    if pulp.LpStatus[model.status] == 'Optimal':
        total_cost = pulp.value(model.objective)
        print(f"Total Annual Cost: ${total_cost:,.2f}")
        print("-" * 40)
        
        print("Selected Warehouses:")
        for w in W_IDs:
            if y[w].varValue == 1.0:
                print(f"- {w}")
        
        print("\nDistribution Plan (Annual Units):")
        for w in W_IDs:
            if y[w].varValue == 1.0:
                print(f"\nFrom {w}:")
                for f in F_IDs:
                    shipped = X[(w, f)].varValue
                    if shipped > 0:
                        print(f"  -> {f}: {shipped:,.0f} units")
    else:
        print("A feasible optimal solution could not be found within the constraints.")

if __name__ == "__main__":
    run_optimization()