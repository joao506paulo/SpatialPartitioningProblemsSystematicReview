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


# Number of regions
NUM_OF_REGIONS = 2
# number of units
NUM_UNITS = len(municipalities)
# number of particles 
NUM_OF_PARTICLES = 200 #200

swarm = []

def atualiza_particao (partition_list):
    partition_list.clear()
    for j in range(NUM_UNITS):
        partition_list.append(math.ceil(particle_position[j]*NUM_OF_REGIONS))#conferir esse append

#inicialização
for i in range(NUM_OF_PARTICLES):
    particle_position = []
    for j in range(NUM_UNITS):
        particle_position.append(random.random())
    particle_velocity = []
    for j in range(NUM_UNITS):
        particle_velocity.append(random.random())
    partition_list = []
    atualiza_particao(partition_list)
    f1 = func_1(municipalities, mun_list, partition_list)
    swarm.append({"posicoes" : particle_position, "velocidade" : particle_velocity, "particoes" : partition_list, "f1" : f1})
    
min_f1 = 1000000
f1_best = 0
for i in range(NUM_OF_PARTICLES):
    if(swarm[i]["f1"] < min_f1):
        gBest = swarm[i]["posicoes"]
        f1_best = swarm[i]["f1"]
    pBest = swarm[i]["posicoes"]

print("comeco")
print(f1_best)
#print(gBest)
#pergunta: w, c_1e2, r_1e2 são escolhidos aleatoriamente? e o que colocar em pBest e gBest
w = 0.5 #0.3
c_1 = 0.3 # 0.15
c_2 = 0.2 #0.1

#função que atualiza a velocidade da partícula
def atualiza_v_i (v_i_t, pBest, gBest, x_i):
    res = w*v_i_t + c_1*random.random()*(pBest - x_i) + c_2*random.random()*(gBest - x_i) 
    return res

#função que atualiza a posição da partícula
def atualiza_x_i (x_i_t, pBest, gBest, v_i_t):
    vel = atualiza_v_i(v_i_t, pBest, gBest, x_i_t)
    res = x_i_t + vel
    return res, vel

def atualiza_particao (swarm):
    swarm["particoes"].clear()
    for j in range(NUM_UNITS):
        swarm["particoes"].append(math.ceil(swarm["posicoes"][j]*NUM_OF_REGIONS))

for k in range(3000): #3000
    for i in swarm:
        for j in range(NUM_UNITS):
            i["posicoes"][j], i["velocidade"][j] = atualiza_x_i(i["posicoes"][j], pBest[j], gBest[j], i["velocidade"][j]) 
        atualiza_particao(i)
        f1 = func_1(municipalities, mun_list, i["particoes"])
        if f1 < i["f1"]:
            pBest = i["posicoes"]
            i["f1"] = f1
        if f1 < f1_best:
            f1_best = f1
            print("atualizou")
            print(f1_best)
            gBest = i["posicoes"]

        
res = []
i = 0
for a in gBest:
    res.append(math.ceil(a))
    i = i+1
print(res)
print(f1_best)

func_1(municipalities, mun_list, [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 2, 1, 2, 2])
base = plotRegionalization(stateMap, res, showCentroids=False, showBoundary=True)
plt.show()
#a resposta não está correta, devo procurar o que está causando o erro
#Não Apagar
regionalization = [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1]
base = plotRegionalization(stateMap, regionalization, showCentroids=False, showBoundary=True)