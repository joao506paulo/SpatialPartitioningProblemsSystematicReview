from utils import workWithStateData, add_medical_procedures, isFeasible, computeDistanceMatrix, dominance_ranking, calculate_crowding_distance, crowded_binary_tournament
#from genetic_algorithm_steiner import mount_solution_from_genotype
import gurobipy as gp
from gurobipy import GRB
import random
import math
from funcoes_objetivo import func_1, func_2, func_3, funcoes_objetivo
import matplotlib.pyplot as plt


file_state_data = "../data/State_Roraima/Municipios_RR.xlsx"
nrows_file_state_data = 16
file_state_map_json = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.json"
object_name = "RR_Municipios_2022"
file_state_map_shapefile = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.shp"
file_medical_procedures = "../data/State_Roraima/Procedimentos_RR.xlsx"
nrows_file_medical_procedures = 964
NUM_OF_REGIONS = 2

### Load state data
stateMap, municipalities, mun_list, stateArea, statePop, arcs = workWithStateData(file_state_data, nrows_file_state_data, file_state_map_json, object_name, file_state_map_shapefile)
add_medical_procedures(municipalities, file_medical_procedures, nrows_file_medical_procedures)
distances = computeDistanceMatrix(municipalities)

# Number of regions
NUM_OF_REGIONS = 2
# number of units
NUM_UNITS = len(municipalities)
# number of particles 
NUM_OF_PARTICLES = 5 #200

def plotRegionalization(mapa, regioes, showCentroids, showBoundary):
    
    mapa = mapa.copy()
    mapa.insert(2, "REGIAO", regioes, True)
    
    #Plot map of regions
    base = mapa.plot(column="REGIAO", figsize=(10, 10), cmap="tab20", categorical=True)
   
    if showBoundary:
        #Acentuar as fronteiras
        base = mapa.boundary.plot(ax=base, color="white")
    
    if showCentroids:
        #Printar os centroides
        base = mapa.centroid.plot(ax=base, color="blue", markersize=7)
            
    return base

base = plotRegionalization(stateMap, [1, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 2], showCentroids=False, showBoundary=True)
plt.show()