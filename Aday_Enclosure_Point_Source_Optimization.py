fprintf("Ryan Aday\nEnclosure Point Source Optimizer\n");
fprintf("Version 1.0\n");

fprintf("Optimizes enclosure dimensions, wall thickness accounting for material selection, environmental factors, etc.\n");

try:
    import numpy as np
    from scipy.optimize import minimize
except ImportError:
    sys.exit("""
        You need the numpy and scipy libraries.
        To install these libraries, please enter:
        pip install numpy scipy
        """);

# Constants
k = 0.02  # Thermal conductivity of the enclosure material (W/m·K), example value

# Function to calculate the temperature at a specific point in the enclosure
def temperature_at_point(x, y, z, enclosure_dims, wall_thickness, flow_rate, heat_source, source_position, env_temp):
    length, width, height = enclosure_dims
    source_x, source_y, source_z = source_position
    
    # Distance from the heat source
    distance = np.sqrt((x - source_x)**2 + (y - source_y)**2 + (z - source_z)**2)
    
    # Simplified temperature calculation based on inverse-square law (for point source)
    if distance == 0:
        distance = 0.01  # To avoid division by zero
    
    temp_increase = heat_source / (4 * np.pi * k * distance)
    
    return env_temp + temp_increase

# Function to calculate the average temperature inside the enclosure
def calculate_average_temperature(enclosure_dims, wall_thickness, flow_rate, heat_source, source_position, env_temp):
    length, width, height = enclosure_dims
    num_points = 10  # Number of points for averaging temperature
    
    total_temp = 0
    for i in np.linspace(0, length, num_points):
        for j in np.linspace(0, width, num_points):
            for k in np.linspace(0, height, num_points):
                total_temp += temperature_at_point(i, j, k, enclosure_dims, wall_thickness, flow_rate, heat_source, source_position, env_temp)
    
    average_temp = total_temp / (num_points**3)
    
    return average_temp

# Objective function to minimize the deviation from the target temperature
def objective_function(params, *args):
    target_temp, flow_rate, heat_source, source_position, env_temp = args
    enclosure_dims = params[:3]
    wall_thickness = params[3]
    
    average_temp = calculate_average_temperature(enclosure_dims, wall_thickness, flow_rate, heat_source, source_position, env_temp)
    return abs(average_temp - target_temp)

# Optimization function
def optimize_enclosure(target_temp, flow_rate, heat_source, source_position, env_temp, initial_guess):
    args = (target_temp, flow_rate, heat_source, source_position, env_temp)
    result = minimize(objective_function, initial_guess, args=args, method='BFGS')
    return result

# Example usage
target_temp = 300  # K
flow_rate = 100  # CFM, example value
heat_source = 1000  # J, example value
source_position = (0.5, 0.5, 0.5)  # Middle of the enclosure
env_temp = 298  # K, example value
initial_guess = [1.0, 1.0, 1.0, 0.1]  # Initial guess for length, width, height, wall thickness

result = optimize_enclosure(target_temp, flow_rate, heat_source, source_position, env_temp, initial_guess)

print(f"Optimal Dimensions (LxWxH): {result.x[:3]}")
print(f"Optimal Wall Thickness: {result.x[3]}")
print(f"Achieved Average Temperature: {calculate_average_temperature(result.x[:3], result.x[3], flow_rate, heat_source, source_position, env_temp)}")
