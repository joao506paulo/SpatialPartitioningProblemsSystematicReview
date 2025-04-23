from utils import workWithStateData, computeDistanceMatrix, plotRegionalizationLabelingModel, djikstraDistance, plotRegionalization
import gurobipy as gp
from gurobipy import GRB
import random
import math
from funcoes_objetivo import func_1
import matplotlib.pyplot as plt

file_state_data = "../data/State_Roraima/Municipios_RR.xlsx"
nrows_file_state_data = 168
file_state_map_json = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.json"
object_name = "RR_Municipios_2022"
file_state_map_shapefile = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.shp"

### Load state data
stateMap, municipalities, mun_list, stateArea, statePop, arcs = workWithStateData(file_state_data, nrows_file_state_data, file_state_map_json, object_name, file_state_map_shapefile)
 
 
regionalization = [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1]
base = plotRegionalization(stateMap, regionalization, showCentroids=False, showBoundary=True)

plt.show()
