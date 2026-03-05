import pulp
import pandas as pd
import folium

def run_optimization():
    print("🚀 Initializing Optimization Engine...\n")


    # 1. DATA INGESTION & PROCESSING

    try:
        facilities = pd.read_csv('../data/facilities.csv')
        warehouses = pd.read_csv('../data/warehouses.csv')
        transport = pd.read_csv('../data/transportation_costs.csv')
    except FileNotFoundError:
        print("❌ Error: Ensure facilities.csv, warehouses.csv, and transportation_costs.csv are in the /data folder.")
        return

    W_IDs = warehouses['Warehouse_ID'].tolist()
    F_IDs = facilities['Facility_ID'].tolist()

    # Dictionaries for optimization
    demand_dict = dict(zip(facilities['Facility_ID'], facilities['Daily_Demand']))
    cap_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Daily_Capacity']))
    construct_cost_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Construction_Cost']))
    op_cost_dict = dict(zip(warehouses['Warehouse_ID'], warehouses['Operational_Cost/Day']))

    transport_dict = {}
    for _, row in transport.iterrows():
        transport_dict[(row['Warehouse_ID'], row['Facility_ID'])] = row['Cost']

    # Dynamic Coordinate Extraction
    facility_coords = {row['Facility_ID']: [row['Latitude'], row['Longitude']] for _, row in facilities.iterrows()}
    warehouse_coords = {row['Warehouse_ID']: [row['Latitude'], row['Longitude']] for _, row in warehouses.iterrows()}

    # 2. MILP OPTIMIZATION MODEL

    model = pulp.LpProblem("Campus_Emergency_Supply_Distribution", pulp.LpMinimize)

    # Decision Variables
    y = pulp.LpVariable.dicts("Open_WH", W_IDs, cat='Binary')
    X = pulp.LpVariable.dicts("Ship_Flow", [(w, f) for w in W_IDs for f in F_IDs], lowBound=0, cat='Continuous')

    # Objective Function
    annual_fixed_costs = pulp.lpSum([((construct_cost_dict[w] / 10) + (365 * op_cost_dict[w])) * y[w] for w in W_IDs])
    annual_transport_costs = pulp.lpSum([transport_dict[(w, f)] * X[(w, f)] for w in W_IDs for f in F_IDs])
    model += annual_fixed_costs + annual_transport_costs, "Total_Annual_Cost"

    # Constraints
    model += pulp.lpSum([y[w] for w in W_IDs]) == 2, "Select_Exactly_Two_Warehouses"
    
    for f in F_IDs:
        model += pulp.lpSum([X[(w, f)] for w in W_IDs]) == 365 * demand_dict[f], f"Demand_Satisfaction_{f}"
        
    for w in W_IDs:
        model += pulp.lpSum([X[(w, f)] for f in F_IDs]) <= 365 * cap_dict[w] * y[w], f"Capacity_Limit_{w}"
        
    model += (annual_fixed_costs + annual_transport_costs) <= 1500000, "Budget_Limit"

    # Solve
    model.solve()

    # 3. BUSINESS ANALYTICS & TERMINAL OUTPUT
    if pulp.LpStatus[model.status] != 'Optimal':
        print("❌ A feasible optimal solution could not be found within the constraints.")
        return

    total_cost = pulp.value(model.objective)
    total_units_delivered = sum(365 * demand_dict[f] for f in F_IDs)
    avg_cost_per_unit = total_cost / total_units_delivered
    remaining_budget = 1500000 - total_cost

    print("✅ OPTIMIZATION SUCCESSFUL")
    print("-" * 50)
    print(f"💰 Total Annual Cost:      ${total_cost:,.2f}")
    print(f"📦 Total Units Delivered:  {total_units_delivered:,.0f} units")
    print(f"📈 Avg. Cost Per Unit:     ${avg_cost_per_unit:,.2f} / unit")
    print(f"🏦 Remaining Budget:       ${remaining_budget:,.2f}\n")

    print("🏢 Warehouse Utilization Report:")
    print("-" * 50)
    for w in W_IDs:
        is_open = y[w].varValue == 1.0
        if is_open:
            used_cap = sum(X[(w, f)].varValue for f in F_IDs)
            max_cap = 365 * cap_dict[w]
            utilization = (used_cap / max_cap) * 100
            print(f" - {w} | OPEN   | Utilization: {utilization:.1f}%")
        else:
            print(f" - {w} | CLOSED | Utilization: 0.0%")

    print("\n🚚 Optimal Routing Plan:")
    print("-" * 50)
    for w in W_IDs:
        if y[w].varValue == 1.0:
            for f in F_IDs:
                shipped = X[(w, f)].varValue
                if shipped > 0:
                    print(f"   {w} ➔ {f} : {shipped:,.0f} units")

    # ==========================================
    # 4. INTERACTIVE MAP GENERATION
    # ==========================================
    print("\n🗺️ Generating Interactive Map...")
    
    # Center map on average campus coordinates
    center_lat = sum(coords[0] for coords in facility_coords.values()) / len(facility_coords)
    center_lon = sum(coords[1] for coords in facility_coords.values()) / len(facility_coords)
    campus_map = folium.Map(location=[center_lat, center_lon], zoom_start=15)

    # Plot Facilities
    for f in F_IDs:
        folium.CircleMarker(
            location=facility_coords[f],
            radius=8,
            color="blue",
            fill=True, fill_opacity=0.8,
            tooltip=f"Facility: {f} (Demand: {demand_dict[f]}/day)"
        ).addTo(campus_map)

    # Find maximum flow for dynamic line weighting
    max_flow = max(X[(w, f)].varValue for w in W_IDs for f in F_IDs if X[(w, f)].varValue > 0)

    # Plot Warehouses and Routes
    for w in W_IDs:
        is_open = y[w].varValue == 1.0
        lat, lon = warehouse_coords[w]
        
        if is_open:
            folium.Marker(
                location=[lat, lon],
                tooltip=f"{w} (SELECTED)",
                icon=folium.Icon(color="green", icon="check-circle", prefix="fa")
            ).addTo(campus_map)
            
            # Draw Dynamic Routes
            for f in F_IDs:
                shipped = X[(w, f)].varValue
                if shipped > 0:
                    f_lat, f_lon = facility_coords[f]
                    dynamic_weight = 2 + (shipped / max_flow) * 6
                    
                    folium.PolyLine(
                        locations=[[lat, lon], [f_lat, f_lon]],
                        color="blue",
                        weight=dynamic_weight,
                        opacity=0.7,
                        tooltip=f"{w} ➔ {f}: {shipped:,.0f} units/year"
                    ).addTo(campus_map)
        else:
            folium.Marker(
                location=[lat, lon],
                tooltip=f"{w} (Available)",
                icon=folium.Icon(color="red", icon="times-circle", prefix="fa")
            ).addTo(campus_map)

    map_filename = "optimized_campus_map.html"
    campus_map.save(map_filename)
    print(f"📍 Map saved successfully as '{map_filename}'")

if __name__ == "__main__":
    run_optimization()