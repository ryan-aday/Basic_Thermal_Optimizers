fprintf("Ryan Aday\nHeat Sink Optimizer\n");
fprintf("Version 1.0\n");

fprintf("Optimizes heat sink geometry accounting for material selection, environmental factors, etc.\n");

try:
    import numpy as np
    from scipy.optimize import minimize
except ImportError:
    sys.exit("""
        You need the numpy and scipy libraries.
        To install these libraries, please enter:
        pip install numpy scipy
        """);

# Empirical coefficients for thermal conductivity of air (W/m·K)
A = 0.024
B = 7.74e-5
C = -1.8e-8

# Function to calculate the thermal conductivity of air
def thermal_conductivity_air(T):
    return A + B * T + C * T**2

# Function to calculate the convection coefficient h_air
def convection_coefficient(flow_rate, fin_height, air_density, ambient_temp):
    k_air = thermal_conductivity_air(ambient_temp)
    nu_air = 15.89e-6  # Kinematic viscosity of air (m^2/s) at 25°C
    Pr = 0.71  # Prandtl number for air
    Re = (flow_rate / (fin_height * air_density)) / nu_air
    Nu = 0.023 * Re**0.8 * Pr**0.3
    h_air = Nu * k_air / fin_height
    return h_air

# Function to calculate the thermal resistance of a single fin
def fin_thermal_resistance(fin_height, fin_thickness, fin_spacing, fin_length, thermal_conductivity, h_air):
    fin_area = 2 * (fin_height * fin_thickness) + 2 * (fin_height * fin_length)
    fin_perimeter = 2 * (fin_thickness + fin_length)
    
    # Fin efficiency (assuming rectangular fins)
    m = np.sqrt(2 * h_air / (thermal_conductivity * fin_thickness))
    fin_efficiency = np.tanh(m * fin_height) / (m * fin_height)
    
    # Thermal resistance of a single fin
    R_fin = 1 / (h_air * fin_efficiency * fin_area)
    
    return R_fin

# Function to calculate the overall thermal resistance of the heat sink
def heat_sink_thermal_resistance(num_fins, fin_height, fin_thickness, fin_spacing, base_thickness, base_length, base_width, thermal_conductivity, flow_rate, air_density, ambient_temp):
    fin_length = base_length - fin_spacing * (num_fins - 1)
    h_air = convection_coefficient(flow_rate, fin_height, air_density, ambient_temp)
    fin_resistance = fin_thermal_resistance(fin_height, fin_thickness, fin_spacing, fin_length, thermal_conductivity, h_air)
    
    # Thermal resistance of the base
    base_area = base_length * base_width
    R_base = base_thickness / (thermal_conductivity * base_area)
    
    # Overall thermal resistance of the heat sink
    R_total = 1 / (num_fins / fin_resistance + 1 / R_base)
    
    return R_total

# Function to calculate the temperature of the heat sink
def calculate_heat_sink_temperature(heat_load, ambient_temp, num_fins, fin_height, fin_thickness, fin_spacing, base_thickness, base_length, base_width, thermal_conductivity, flow_rate, air_density):
    R_total = heat_sink_thermal_resistance(num_fins, fin_height, fin_thickness, fin_spacing, base_thickness, base_length, base_width, thermal_conductivity, flow_rate, air_density, ambient_temp)
    heat_sink_temp = ambient_temp + heat_load * R_total
    
    return heat_sink_temp

# Objective function to minimize the temperature of the heat sink
def objective_function(params, *args):
    heat_load, ambient_temp, thermal_conductivity, target_temp, flow_rate, air_density = args
    num_fins, fin_height, fin_thickness, fin_spacing, base_thickness, base_length, base_width = params
    
    heat_sink_temp = calculate_heat_sink_temperature(heat_load, ambient_temp, num_fins, fin_height, fin_thickness, fin_spacing, base_thickness, base_length, base_width, thermal_conductivity, flow_rate, air_density)
    return abs(heat_sink_temp - target_temp)

# Optimization function
def optimize_heat_sink(target_temp, heat_load, ambient_temp, thermal_conductivity, flow_rate, air_density, initial_guess):
    args = (heat_load, ambient_temp, thermal_conductivity, target_temp, flow_rate, air_density)
    result = minimize(objective_function, initial_guess, args=args, method='BFGS')
    return result

# Example usage
target_temp = 310  # K
heat_load = 50  # W, example value
ambient_temp = 298  # K, example value
thermal_conductivity = 200  # W/m·K, example value for aluminum
flow_rate = 0.01  # m^3/s, example value
air_density = 1.2  # kg/m^3, example value at room temperature
initial_guess = [10, 0.05, 0.002, 0.005, 0.01, 0.1, 0.1]  # Initial guess for number of fins, fin height, fin thickness, fin spacing, base thickness, base length, base width

result = optimize_heat_sink(target_temp, heat_load, ambient_temp, thermal_conductivity, flow_rate, air_density, initial_guess)

print(f"Optimal Number of Fins: {result.x[0]}")
print(f"Optimal Fin Height: {result.x[1]} m")
print(f"Optimal Fin Thickness: {result.x[2]} m")
print(f"Optimal Fin Spacing: {result.x[3]} m")
print(f"Optimal Base Thickness: {result.x[4]} m")
print(f"Optimal Base Length: {result.x[5]} m")
print(f"Optimal Base Width: {result.x[6]} m")
print(f"Achieved Heat Sink Temperature: {calculate_heat_sink_temperature(heat_load, ambient_temp, *result.x, thermal_conductivity, flow_rate, air_density)} K")
