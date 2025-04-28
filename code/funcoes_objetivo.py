from utils import workWithStateData, computeDistanceMatrix, plotRegionalizationLabelingModel, djikstraDistance
import gurobipy as gp
from gurobipy import GRB

file_state_data = "../data/State_Roraima/Municipios_RR.xlsx"
nrows_file_state_data = 168
file_state_map_json = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.json"
object_name = "RR_Municipios_2022"
file_state_map_shapefile = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.shp"

### Load state data
stateMap, municipalities, mun_list, stateArea, statePop, arcs = workWithStateData(file_state_data, nrows_file_state_data, file_state_map_json, object_name, file_state_map_shapefile)


# Number of regions
NUM_OF_REGIONS = 2
# number of units
NUM_UNITS = len(municipalities)
#lista para teste
partition_list = [0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]

#Primeira função objetivo (a ser minimizada)
def func_1 (municipalities, mun_list, partition_list):
    #calculo de average number of inhabitants por microregion
    #print(partition_list)
    total = 0
    for i in mun_list:
        total += municipalities[i]['NUM_HABITANTES']
    H = total/NUM_OF_REGIONS
    #print("H = ", end='')
    #print(H)

    soma_l = 0
    for l in range(NUM_OF_REGIONS):
        soma_i = 0
        for i in range(NUM_UNITS):
            if partition_list[i] == l:
                soma_i+= municipalities[mun_list[i]]['NUM_HABITANTES']
                #print("Soma_i = ", end='')
                #print(soma_i)
        soma_i = soma_i - H
        if soma_i < 0:
            soma_i = soma_i* (-1)
        soma_l = soma_i
        #print("Soma_l = ", end='')
        #print(soma_l)
    f1 = soma_l / NUM_OF_REGIONS
    #print("f1 = ", end='')
    #print("calculou")
    #print(f1)
    return f1

#func_1(municipalities, mun_list, partition_list)

print(func_1(municipalities, mun_list, [2,2,1,2,2,2,2,2,2,1,2,2,2,2,2]))
print(func_1(municipalities, mun_list, [1,1,2,1,1,1,1,1,1,1,1,1,1,1,1]))
