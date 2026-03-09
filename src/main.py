# ==============================================================================
# CAMPUS LOGISTICS OPTIMIZATION & INTERACTIVE MAPPING
# ==============================================================================

"""
Campus Emergency Supply Distribution Optimizer.

Uses Mixed-Integer Linear Programming (MILP) via PuLP to select optimal
warehouse locations for supplying campus facilities, minimizing total annual
cost while respecting demand, capacity, and budget constraints.
"""

from pathlib import Path

import folium
import pandas as pd
import pulp

# Resolve all paths relative to the project root (parent of /src)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load facility, warehouse, and transportation cost data from CSVs.

    Returns:
        A tuple of (facilities, warehouses, transport) DataFrames.

    Raises:
        FileNotFoundError: If any required CSV file is missing from /data.
    """
    facilities = pd.read_csv(DATA_DIR / "facilities.csv")
    warehouses = pd.read_csv(DATA_DIR / "warehouses.csv")
    transport = pd.read_csv(DATA_DIR / "transportation_costs.csv")
    return facilities, warehouses, transport


def build_and_solve_model(
    facilities: pd.DataFrame,
    warehouses: pd.DataFrame,
    transport: pd.DataFrame,
) -> tuple[pulp.LpProblem, dict, dict, dict, dict, dict, dict, list, list]:
    """Formulate and solve the MILP model for optimal warehouse selection.

    Args:
        facilities: DataFrame with Facility_ID, Daily_Demand, Latitude, Longitude.
        warehouses: DataFrame with Warehouse_ID, Daily_Capacity, costs, coordinates.
        transport: DataFrame with Warehouse_ID, Facility_ID, Cost.

    Returns:
        A tuple containing the solved model, decision variables, and data dicts.
    """
    W_IDs = warehouses["Warehouse_ID"].tolist()
    F_IDs = facilities["Facility_ID"].tolist()

    # Build lookup dictionaries
    demand = dict(zip(facilities["Facility_ID"], facilities["Daily_Demand"]))
    capacity = dict(zip(warehouses["Warehouse_ID"], warehouses["Daily_Capacity"]))
    construct_cost = dict(zip(warehouses["Warehouse_ID"], warehouses["Construction_Cost"]))
    op_cost = dict(zip(warehouses["Warehouse_ID"], warehouses["Operational_Cost/Day"]))

    transport_cost: dict[tuple[str, str], float] = {}
    for _, row in transport.iterrows():
        transport_cost[(row["Warehouse_ID"], row["Facility_ID"])] = row["Cost"]

    # --- MILP Model ---
    model = pulp.LpProblem("Campus_Emergency_Supply_Distribution", pulp.LpMinimize)

    # Decision Variables
    y = pulp.LpVariable.dicts("Open_WH", W_IDs, cat="Binary")
    X = pulp.LpVariable.dicts(
        "Ship_Flow", [(w, f) for w in W_IDs for f in F_IDs], lowBound=0, cat="Continuous"
    )

    # Objective: minimize total annual cost
    annual_fixed = pulp.lpSum(
        [((construct_cost[w] / 10) + (365 * op_cost[w])) * y[w] for w in W_IDs]
    )
    annual_transport = pulp.lpSum(
        [transport_cost[(w, f)] * X[(w, f)] for w in W_IDs for f in F_IDs]
    )
    model += annual_fixed + annual_transport, "Total_Annual_Cost"

    # Constraints
    model += pulp.lpSum([y[w] for w in W_IDs]) == 2, "Select_Exactly_Two_Warehouses"

    for f in F_IDs:
        model += (
            pulp.lpSum([X[(w, f)] for w in W_IDs]) == 365 * demand[f],
            f"Demand_Satisfaction_{f}",
        )

    for w in W_IDs:
        model += (
            pulp.lpSum([X[(w, f)] for f in F_IDs]) <= 365 * capacity[w] * y[w],
            f"Capacity_Limit_{w}",
        )

    model += (annual_fixed + annual_transport) <= 1500000, "Budget_Limit"

    # Solve
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    return model, y, X, demand, capacity, construct_cost, op_cost, W_IDs, F_IDs


def print_results(
    model: pulp.LpProblem,
    y: dict,
    X: dict,
    demand: dict[str, int],
    capacity: dict[str, int],
    W_IDs: list[str],
    F_IDs: list[str],
) -> None:
    """Print optimization results, warehouse utilization, and routing plan."""
    if pulp.LpStatus[model.status] != "Optimal":
        print("A feasible optimal solution could not be found within the constraints.")
        return

    total_cost = pulp.value(model.objective)
    total_units = sum(365 * demand[f] for f in F_IDs)
    avg_cost = total_cost / total_units
    remaining = 1500000 - total_cost

    print("OPTIMIZATION SUCCESSFUL")
    print("-" * 50)
    print(f"  Total Annual Cost:      ${total_cost:,.2f}")
    print(f"  Total Units Delivered:  {total_units:,.0f} units")
    print(f"  Avg. Cost Per Unit:     ${avg_cost:,.2f} / unit")
    print(f"  Remaining Budget:       ${remaining:,.2f}\n")

    print("Warehouse Utilization Report:")
    print("-" * 50)
    for w in W_IDs:
        if y[w].varValue == 1.0:
            used = sum(X[(w, f)].varValue for f in F_IDs)
            max_cap = 365 * capacity[w]
            util = (used / max_cap) * 100
            print(f"  - {w} | OPEN   | Utilization: {util:.1f}%")
        else:
            print(f"  - {w} | CLOSED | Utilization: 0.0%")

    print("\nOptimal Routing Plan:")
    print("-" * 50)
    for w in W_IDs:
        if y[w].varValue == 1.0:
            for f in F_IDs:
                shipped = X[(w, f)].varValue
                if shipped > 0:
                    print(f"  {w} -> {f} : {shipped:,.0f} units")


def generate_map(
    facilities: pd.DataFrame,
    warehouses: pd.DataFrame,
    y: dict,
    X: dict,
    demand: dict[str, int],
    W_IDs: list[str],
    F_IDs: list[str],
) -> None:
    """Generate an interactive Folium map showing optimized routes.

    The map is saved to the /output directory in the project root.

    Args:
        facilities: Facilities DataFrame (must include Latitude, Longitude).
        warehouses: Warehouses DataFrame (must include Latitude, Longitude).
        y: Warehouse open/close binary decision variables.
        X: Shipment flow continuous decision variables.
        demand: Dict mapping Facility_ID to daily demand.
        W_IDs: List of warehouse IDs.
        F_IDs: List of facility IDs.
    """
    facility_coords = {
        row["Facility_ID"]: [row["Latitude"], row["Longitude"]]
        for _, row in facilities.iterrows()
    }
    warehouse_coords = {
        row["Warehouse_ID"]: [row["Latitude"], row["Longitude"]]
        for _, row in warehouses.iterrows()
    }

    # Center map on average campus coordinates
    center_lat = sum(c[0] for c in facility_coords.values()) / len(facility_coords)
    center_lon = sum(c[1] for c in facility_coords.values()) / len(facility_coords)
    campus_map = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    # Plot Facilities
    for f in F_IDs:
        folium.CircleMarker(
            location=facility_coords[f],
            radius=8,
            color="blue",
            fill=True,
            fill_opacity=0.8,
            tooltip=f"Facility: {f} (Demand: {demand[f]}/day)",
        ).add_to(campus_map)

    # Find maximum flow for dynamic line weighting
    positive_flows = [X[(w, f)].varValue for w in W_IDs for f in F_IDs if X[(w, f)].varValue > 0]
    max_flow = max(positive_flows) if positive_flows else 1

    # Plot Warehouses and Routes
    for w in W_IDs:
        lat, lon = warehouse_coords[w]

        if y[w].varValue == 1.0:
            folium.Marker(
                location=[lat, lon],
                tooltip=f"{w} (SELECTED)",
                icon=folium.Icon(color="green", icon="check-circle", prefix="fa"),
            ).add_to(campus_map)

            # Draw dynamic routes
            for f in F_IDs:
                shipped = X[(w, f)].varValue
                if shipped > 0:
                    f_lat, f_lon = facility_coords[f]
                    weight = 2 + (shipped / max_flow) * 6

                    folium.PolyLine(
                        locations=[[lat, lon], [f_lat, f_lon]],
                        color="blue",
                        weight=weight,
                        opacity=0.7,
                        tooltip=f"{w} -> {f}: {shipped:,.0f} units/year",
                    ).add_to(campus_map)
        else:
            folium.Marker(
                location=[lat, lon],
                tooltip=f"{w} (Available)",
                icon=folium.Icon(color="red", icon="times-circle", prefix="fa"),
            ).add_to(campus_map)

    # Save map to /output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    map_path = OUTPUT_DIR / "optimized_campus_map.html"
    campus_map.save(str(map_path))
    print(f"\nMap saved successfully as '{map_path}'")


def run_optimization() -> None:
    """Entry point: load data, solve MILP, print results, and generate map."""
    print("Initializing Optimization Engine...\n")

    try:
        facilities, warehouses, transport = load_data()
    except FileNotFoundError:
        print(
            "Error: Ensure facilities.csv, warehouses.csv, and "
            "transportation_costs.csv are in the /data folder."
        )
        return

    model, y, X, demand, capacity, _, _, W_IDs, F_IDs = build_and_solve_model(
        facilities, warehouses, transport
    )

    if pulp.LpStatus[model.status] != "Optimal":
        print("A feasible optimal solution could not be found within the constraints.")
        return

    print_results(model, y, X, demand, capacity, W_IDs, F_IDs)
    generate_map(facilities, warehouses, y, X, demand, W_IDs, F_IDs)


if __name__ == "__main__":
    run_optimization()