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

swarm = []


#método de contiguidade
def contiguo (municipalities, mun_list, partition_list):
    list = []
    maiores = []
    resposta = []
    for a in range(NUM_UNITS):
        list.append(0)
        resposta.append(0)
    #solucoes = mount_solution_from_genotype(partition_list, municipalities, NUM_OF_REGIONS, statePop) 
    #eh_contiguo = isFeasible(solucoes, NUM_OF_REGIONS, municipalities)
    #if eh_contiguo:
        #print("é contíguo")
        #return

    for l in range(NUM_OF_REGIONS+1): #acho que posso estar escolhendo duas unidades da mesma região, se isso tiver acontecendo, estou com problemas aqui
        for i in range(NUM_UNITS):
            cont = 0
            if partition_list[i] == l+1:
                for j in municipalities[mun_list[i]]['vizinhos']:
                    k = mun_list.index(j)     #ver posicao de j em partition list
                    if partition_list[k] == l+1:
                        cont = cont +1
            list[i] = cont
        
        maior_valor = 0
        maior_indice = 0
    for l in range(NUM_OF_REGIONS+1):
        for i in range(NUM_UNITS):
            if list[i] > maior_valor and partition_list[i] == l+1:
                maior_valor = list[i]
                maior_indice = i
        maiores.append(maior_indice)
        list[maior_indice] = 0
        #print(list)        
    #print(maiores)

    #estou na parte depois uso a matriz...
    #não sei o que fazer: preciso passar por todos os municípios e verificar quantos vizinhos estão na mesma região
    #esse laço está errado, preciso passar por todos os vizinhos dos centros de cada região e descobrir o menor e adicionar 
    #a resposta e repetir isso até adicionar todas as unidades
    matriz = computeDistanceMatrix(municipalities)
    for i in range(NUM_UNITS):
        menor_valor = 1000000
        for j in range(NUM_OF_REGIONS):
            id_centro = mun_list[maiores[j]]
            for v in municipalities[id_centro]['vizinhos']:
                id_vizinho = v
                valor = matriz[(id_centro), (id_vizinho)]
                if valor < menor_valor:
                    menor_valor = valor
                    vizinho = id_vizinho
                    centro = id_centro
        a = mun_list.index(centro)
        l = partition_list[a]
        resposta[a] = l
        b = mun_list.index(vizinho)
        resposta[b] = l 
        matriz[(centro),(vizinho)] = 1000000
    #print(resposta)
    return resposta

#copiado do utils anterior
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
    contiguo(municipalities, mun_list, partition_list)
    resposta = funcoes_objetivo(municipalities, mun_list, partition_list)
    swarm.append({"posicoes" : particle_position, "velocidade" : particle_velocity, "particoes" : partition_list, "f1" : resposta['f1'], "f2" : resposta['f2'], "f3" : resposta['f3']})


min_f1 = float("inf")
f1_best = 0

#print(gBest)
def atualiza_pareto_set(swarm, pareto):
    min_f1 = float("inf")
    max_f2 = 0
    min_f3 = float("inf")
    pareto.append(swarm[0])
    for i in pareto:
        if i["f1"] < min_f1:
            min_f1 = i["f1"]
        if i["f2"] > max_f2:
            max_f2 = i["f2"]
        if i["f3"] < min_f3:
            min_f3 = i["f3"]
    #solucao = {"f1_best" : 0, "f2_best" : 0, "f3_best" : 0, "gBest" : swarm[0]}
    for i in range(NUM_OF_PARTICLES):
        #domina o conjunto pareto ótimo?
        if swarm[i]["f1"] < min_f1 and swarm[i]["f2"] > max_f2 and swarm[i]["f3"] < min_f3:
            pareto.clear()
            pareto.append(swarm[i])
            min_f1 = swarm[i]["f1"]
            max_f2 = swarm[i]["f2"]
            min_f3 = swarm[i]["f3"]
        #não é dominada pelo conjunto pareto ótimo?
        if not(swarm[i]["f1"] > min_f1 and swarm[i]["f2"] < max_f2 and swarm[i]["f3"] > min_f3):
            pareto.append(swarm[i])
            if swarm[i]["f1"] < min_f1:
                min_f1 = swarm[i]["f1"]
            if swarm[i]["f2"] > max_f2:
                max_f2 = swarm[i]["f2"]
            if swarm[i]["f3"] < min_f3:
                min_f3 = swarm[i]["f3"]

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
        swarm["particoes"].append(math.ceil(swarm["posicoes"][j])*NUM_OF_REGIONS)





#base = plotRegionalization(stateMap, [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], showCentroids=False, showBoundary=True)
#plt.show()

#r = contiguo(municipalities, mun_list, [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1])

#base = plotRegionalization(stateMap, r, showCentroids=False, showBoundary=True)
#plt.show()


pareto = []
atualiza_pareto_set(swarm, pareto)
gBest = random.choice(pareto)
pBest = []
for i in range(NUM_OF_PARTICLES):
    pBest = pBest + [swarm[i]['posicoes']]

#print(pBest)
#resposta = funcoes_objetivo(municipalities, mun_list, i["particoes"])
#loop do algoritmo enxame de partículas
#preciso revisar pBest e gBest e a ordem das atividades
for k in range(10): #3000
    print(k)
    for i in range(NUM_OF_PARTICLES):
        for j in range(NUM_UNITS):
            #print(type(swarm[i]["posicoes"][j]))
            #print(type(pBest[i]["posicoes"]))
            swarm[i]["posicoes"][j], swarm[i]["velocidade"][j] = atualiza_x_i(swarm[i]["posicoes"][j], pBest[i][j], gBest['posicoes'][j], swarm[i]["velocidade"][j]) 
        atualiza_particao(swarm[i])
        print("Não contíguo")
        print(swarm[i]['particoes'])
        swarm[i]['particoes'] = contiguo(municipalities, mun_list, swarm[i]['particoes'])
        print("Contíguo")
        print(swarm[i]['particoes'])
        resposta = funcoes_objetivo(municipalities, mun_list, swarm[i]["particoes"])
        if resposta['f1'] < swarm[i]["f1"] and resposta['f2'] > swarm[i]["f2"] and resposta['f3'] < swarm[i]["f3"]:
            pBest[i] = swarm[i]["posicoes"]
            swarm[i]["f1"] = resposta['f1']
            swarm[i]["f2"] = resposta['f2']
            swarm[i]["f3"] = resposta['f3']
        elif not(swarm[i]["f1"] < resposta['f1'] and swarm[i]["f2"] > resposta['f2'] and swarm[i]["f3"] < resposta['f3']):
            if random.choice([True, False]):
                pBest[i] = swarm[i]["posicoes"]
                swarm[i]["f1"] = resposta['f1']
                swarm[i]["f2"] = resposta['f2']
                swarm[i]["f3"] = resposta['f3']

        atualiza_pareto_set(swarm, pareto)
        gBest = random.choice(pareto) #apenas uma versão para teste

        
res = []
for a in pareto:
    sub_list = []
    for b in a["posicoes"]:
        sub_list.append(math.ceil(b))
    res.append(sub_list)

for a in range(len(res)):
    res[a] = contiguo(municipalities, mun_list, res[a])

nome_arquivo = "saida.txt"

with open(nome_arquivo,"w") as f:
    for sublista in res:
        f.write(",".join(map(str, sublista)) + "\n")
print(f"Dados salvos em '{nome_arquivo}'")

#func_1(municipalities, mun_list, [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 2, 1, 2, 2])

#for i in res:
    #base = plotRegionalization(stateMap, i, showCentroids=False, showBoundary=True)
    #plt.show()
#a resposta não está correta, devo procurar o que está causando o erro
#Não Apagar
#regionalization = [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1]
#base = plotRegionalization(stateMap, regionalization, showCentroids=False, showBoundary=True)