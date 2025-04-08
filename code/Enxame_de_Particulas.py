from utils import workWithStateData, computeDistanceMatrix, plotRegionalizationLabelingModel, djikstraDistance, plotRegionalization
import gurobipy as gp
from gurobipy import GRB
import random
import math
from funcoes_objetivo import func_1

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
# number of particles 
NUM_OF_PARTICLES = 50

swarm = []

def atualiza_particao (partition_list):
    for j in range(NUM_UNITS):
        partition_list.append(math.ceil(particle_position[j]))

#inicialização
for i in range(NUM_OF_PARTICLES):
    particle_position = []
    for j in range(NUM_UNITS):
        particle_position.append(random.random()*NUM_OF_REGIONS)
    particle_velocity = []
    for j in range(NUM_UNITS):
        particle_velocity.append(random.random()*NUM_OF_REGIONS)
    partition_list = []
    atualiza_particao(partition_list)
    f1 = func_1(municipalities, mun_list, partition_list)
    swarm.append({"posicoes" : particle_position, "velocidade" : particle_velocity, "particoes" : partition_list, "f1" : f1})
    
min_f1 = 1000000
f1_best = 0
for i in range(50):
    if(swarm[i]["f1"] < min_f1):
        gBest = swarm[i]["posicoes"]
        f1_best = swarm[i]["f1"]
    pBest = swarm[i]["posicoes"]

print(f1_best)
print(gBest)
#pergunta: w, c_1e2, r_1e2 são escolhidos aleatoriamente? e o que colocar em pBest e gBest
w = 0.5
c_1 = 0.3
c_2 = 0.2

#função que atualiza a velocidade da partícula
def atualiza_v_i (v_i_t, pBest, gBest, x_i):
    res = w*v_i_t + c_1*random.random()*(pBest - x_i) + c_2*random.random()*(gBest - x_i) 
    return res

#função que atualiza a posição da partícula
def atualiza_x_i (x_i_t, pBest, gBest, v_i_t):
    res = x_i_t + atualiza_v_i(v_i_t, pBest, gBest, x_i_t)
    return res

for i in range(100):
    for i in swarm:
        for j in range(NUM_UNITS):
            atualiza_x_i(i["velocidade"][j], pBest[j], gBest[j], i["posicoes"][j]) 
            atualiza_particao(i["particoes"])
            f1 = func_1(municipalities, mun_list, i["particoes"])
            if f1 < i["f1"]:
                pBest = i["posicoes"]
            if f1 < f1_best:
                gBest = i["posicoes"]

#print(f1_best)        
res = []
i = 0
for a in gBest:
    res.append(math.ceil(a))
    i = i+1
print(res)
#a resposta não está correta, devo procurar o que está causando o erro
#Não Apagar
regionalization = [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1]
base = plotRegionalization(stateMap, regionalization, showCentroids=False, showBoundary=True)