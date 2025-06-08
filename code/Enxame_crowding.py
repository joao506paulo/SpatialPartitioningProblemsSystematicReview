from utils import workWithStateData, add_medical_procedures, isFeasible, computeDistanceMatrix, dominance_ranking, calculate_crowding_distance, crowded_binary_tournament
#from genetic_algorithm_steiner import mount_solution_from_genotype
import gurobipy as gp
from gurobipy import GRB
import random
import math
from funcoes_objetivo import func_1, func_2, func_3, funcoes_objetivo
import matplotlib.pyplot as plt

### Load state data
#Roraima state
#file_state_data = "../data/State_Roraima/Municipios_RR.xlsx"
#nrows_file_state_data = 16
#file_state_map_json = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.json"
#object_name = "RR_Municipios_2022"
#file_state_map_shapefile = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.shp"
#file_medical_procedures = "../data/State_Roraima/Procedimentos_RR.xlsx"
#nrows_file_medical_procedures = 964
#NUM_OF_REGIONS = 2

#Amazonas state
#file_state_data = "../data/State_Amazonas/Municipios_AM.xlsx"
#nrows_file_state_data = 63
#file_state_map_json = "../data/State_Amazonas/AM_Municipios_2022/AM_Municipios_2022.json"
#object_name = "AM_Municipios_2022"
#file_state_map_shapefile = "../data/State_Amazonas/AM_Municipios_2022/AM_Municipios_2022.shp"
#file_medical_procedures = "../data/State_Amazonas/Procedimentos_AM.xlsx"
#nrows_file_medical_procedures = 6890
#NUM_OF_REGIONS = 9

#Rio Grande do Norte state
file_state_data = "../data/State_RioGrandeDoNorte/Municipios_RN.xlsx"
nrows_file_state_data = 168
file_state_map_json = "../data/State_RioGrandeDoNorte/RN_Municipios_2022/RN_Municipios_2022.json"
object_name = "RN_Municipios_2022"
file_state_map_shapefile = "../data/State_RioGrandeDoNorte/RN_Municipios_2022/RN_Municipios_2022.shp"
file_medical_procedures = "../data/State_RioGrandeDoNorte/Procedimentos_RN.xlsx"
nrows_file_medical_procedures = 5345
NUM_OF_REGIONS = 8

### Load state data
stateMap, municipalities, mun_list, stateArea, statePop, arcs = workWithStateData(file_state_data, nrows_file_state_data, file_state_map_json, object_name, file_state_map_shapefile)
add_medical_procedures(municipalities, file_medical_procedures, nrows_file_medical_procedures)
distances = computeDistanceMatrix(municipalities)

# Number of regions
#NUM_OF_REGIONS = 2
# number of units
NUM_UNITS = len(municipalities)
# number of particles 
NUM_OF_PARTICLES = 80 #200

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


def atualiza_particao (particle_data): # Renomeado de swarm para particle_data para clareza
    particle_data["particoes"].clear()
    for j in range(NUM_UNITS):
        # Assegura que o valor esteja entre 0 e 1 antes de multiplicar por NUM_OF_REGIONS
        # e que o resultado seja pelo menos 1 (já que as regiões são 1-indexadas)
        region_val = math.ceil(particle_data["posicoes"][j] * NUM_OF_REGIONS)
        particle_data["particoes"].append(max(1, min(NUM_OF_REGIONS, region_val)))


#inicialização
for i in range(NUM_OF_PARTICLES):
    particle_position = []
    for j in range(NUM_UNITS):
        particle_position.append(random.random())
    particle_velocity = []
    for j in range(NUM_UNITS):
        particle_velocity.append(random.random())
    partition_list = []
    
    # Cria um dicionário temporário para a partícula para usar com atualiza_particao
    temp_particle = {"posicoes": particle_position, "particoes": partition_list}
    atualiza_particao(temp_particle)
    
    partition_list = contiguo(municipalities, mun_list, temp_particle["particoes"]) # Use a partição corrigida
    resposta = funcoes_objetivo(municipalities, mun_list, partition_list)
    swarm.append({"posicoes" : particle_position, "velocidade" : particle_velocity, "particoes" : partition_list, "f1" : resposta['f1'], "f2" : resposta['f2'], "f3" : resposta['f3']})


min_f1 = float("inf")
f1_best = 0

def atualiza_pareto_set(swarm_list, pareto_set):
    # Crie uma lista temporária para as soluções candidatas ao Pareto para a iteração atual
    current_candidates = []
    for particle in swarm_list:
        current_candidates.append({
            "posicoes": particle["posicoes"],
            "velocidade": particle["velocidade"],
            "particoes": particle["particoes"],
            "f1": particle["f1"],
            "f2": particle["f2"],
            "f3": particle["f3"]
        })
    
    # Combine o conjunto Pareto atual com os candidatos
    combined_solutions = pareto_set + current_candidates

    # Encontre o novo conjunto Pareto
    new_pareto_set = []
    for i in range(len(combined_solutions)):
        is_dominated = False
        for j in range(len(combined_solutions)):
            if i != j:
                # Se a solução j domina a solução i
                # Objetivo: f1 (min), f2 (max), f3 (min)
                dominates_f1 = combined_solutions[j]["f1"] < combined_solutions[i]["f1"]
                dominates_f2 = combined_solutions[j]["f2"] > combined_solutions[i]["f2"]
                dominates_f3 = combined_solutions[j]["f3"] < combined_solutions[i]["f3"]

                # Critério de dominância: todas as funções objetivo em uma direção e pelo menos uma estritamente melhor
                if (dominates_f1 and combined_solutions[j]["f2"] >= combined_solutions[i]["f2"] and combined_solutions[j]["f3"] <= combined_solutions[i]["f3"]) or \
                   (dominates_f2 and combined_solutions[j]["f1"] <= combined_solutions[i]["f1"] and combined_solutions[j]["f3"] <= combined_solutions[i]["f3"]) or \
                   (dominates_f3 and combined_solutions[j]["f1"] <= combined_solutions[i]["f1"] and combined_solutions[j]["f2"] >= combined_solutions[i]["f2"]):
                    
                    if (dominates_f1 or dominates_f2 or dominates_f3) and \
                       (combined_solutions[j]["f1"] <= combined_solutions[i]["f1"] and \
                        combined_solutions[j]["f2"] >= combined_solutions[i]["f2"] and \
                        combined_solutions[j]["f3"] <= combined_solutions[i]["f3"]):
                        is_dominated = True
                        break
        if not is_dominated:
            new_pareto_set.append(combined_solutions[i])

    #Remove duplicatas
    seen = set()
    unique_new_pareto_set = []
    for item in new_pareto_set:
        # Para listas, você pode precisar de uma representação hashable ou comparar manualmente
        # Se os itens forem listas de elementos hashable:
        item_tuple = tuple(item['particoes'])
        if item_tuple not in seen:
            seen.add(item_tuple)
            unique_new_pareto_set.append(item)
        # Se os itens forem objetos mais complexos e você precisar de uma comparação personalizada,
        # você precisaria implementar a lógica de comparação aqui.


    pareto_set.clear()
    pareto_set.extend(unique_new_pareto_set)



# Nova função calculate_crowding_distance adaptada para uma lista Pareto
def calculate_crowding_distance(solutions, fitness_keys):
    num_solutions = len(solutions)
    crowding_distances = [0.0] * num_solutions

    if num_solutions <= 2:
        for i in range(num_solutions):
            crowding_distances[i] = float('inf')
        return crowding_distances

    for key in fitness_keys:
        # Ordena os índices das soluções pelo valor da função objetivo atual
        sorted_indices = sorted(range(num_solutions), key=lambda i: solutions[i][key])
        
        f_min = solutions[sorted_indices[0]][key]
        f_max = solutions[sorted_indices[-1]][key]
        range_f = f_max - f_min if f_max != f_min else 1e-9

        # Borda recebe infinito
        crowding_distances[sorted_indices[0]] = float('inf')
        crowding_distances[sorted_indices[-1]] = float('inf')

        # Interiores recebem a soma das distâncias normalizadas
        for j in range(1, num_solutions - 1):
            prev_f = solutions[sorted_indices[j - 1]][key]
            next_f = solutions[sorted_indices[j + 1]][key]
            dist = (next_f - prev_f) / range_f
            if crowding_distances[sorted_indices[j]] != float('inf'): # Evita somar a infinitos
                crowding_distances[sorted_indices[j]] += dist

    return crowding_distances


#pergunta: w, c_1e2, r_1e2 são escolhidos aleatoriamente? e o que colocar em pBest e gBest
w = 0.5 #0.3
c_1 = 0.3 # 0.15
c_2 = 0.2 #0.1

#função que atualiza a velocidade da partícula
def atualiza_v_i (v_i_t, pBest_val, gBest_val, x_i_t): # Renomeei pBest e gBest para evitar conflito com as listas
    res = w*v_i_t + c_1*random.random()*(pBest_val - x_i_t) + c_2*random.random()*(gBest_val - x_i_t) 
    return res

#função que atualiza a posição da partícula
def atualiza_x_i (x_i_t, pBest_val, gBest_val, v_i_t): # Renomeei pBest e gBest para evitar conflito com as listas
    vel = atualiza_v_i(v_i_t, pBest_val, gBest_val, x_i_t)
    res = x_i_t + vel
    # Garante que a posição esteja dentro do intervalo [0, 1]
    res = max(0.0, min(1.0, res))
    return res, vel


#base = plotRegionalization(stateMap, [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], showCentroids=False, showBoundary=True)
#plt.show()

#r = contiguo(municipalities, mun_list, [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1])

#base = plotRegionalization(stateMap, r, showCentroids=False, showBoundary=True)
#plt.show()


pareto = []
atualiza_pareto_set(swarm, pareto)

# Inicialização de pBest e gBest
pBest = []
for i in range(NUM_OF_PARTICLES):
    # pBest deve armazenar a melhor posição encontrada por cada partícula
    # Inicialmente, é a posição atual da partícula
    pBest.append(list(swarm[i]['posicoes'])) 

# gBest é uma solução do conjunto de Pareto
# Seleção de gBest baseada na crowding distance (após a primeira iteração, para diversidade)
# Na primeira iteração, podemos escolher aleatoriamente ou a solução com melhor f1, f2 ou f3 individual
if pareto:
    gBest = random.choice(pareto)
else:
    gBest = None # Tratar o caso onde pareto está vazio

#print(pBest)
#resposta = funcoes_objetivo(municipalities, mun_list, i["particoes"])
#loop do algoritmo enxame de partículas
#preciso revisar pBest e gBest e a ordem das atividades
for k in range(800): #3000
    print(f"Iteração: {k}")
    for i in range(NUM_OF_PARTICLES):
        for j in range(NUM_UNITS):
            # Passa o valor específico da posição de pBest e gBest para a função de atualização
            # Certifique-se que gBest não é None antes de acessar 'posicoes'
            gBest_pos_j = gBest['posicoes'][j] if gBest else random.random() # Fallback se gBest for None
            swarm[i]["posicoes"][j], swarm[i]["velocidade"][j] = atualiza_x_i(
                swarm[i]["posicoes"][j], 
                pBest[i][j], # Acessa a posição j da melhor posição da partícula i
                gBest_pos_j, # Acessa a posição j da melhor posição global
                swarm[i]["velocidade"][j]
            ) 
        
        # Cria um dicionário temporário para a partícula para usar com atualiza_particao
        temp_particle_for_update = {"posicoes": swarm[i]["posicoes"], "particoes": swarm[i]["particoes"]}
        atualiza_particao(temp_particle_for_update)
        swarm[i]["particoes"] = temp_particle_for_update["particoes"] # Atualiza a partição da partícula
        
        #print("Não contíguo")
        #print(swarm[i]['particoes'])
        swarm[i]['particoes'] = contiguo(municipalities, mun_list, swarm[i]['particoes'])
        #print("Contíguo")
        #print(swarm[i]['particoes'])
        
        resposta = funcoes_objetivo(municipalities, mun_list, swarm[i]["particoes"])
        
        # Atualiza pBest
        # Verifica se a nova solução domina o pBest anterior ou é melhor em alguns objetivos
        if resposta['f1'] < swarm[i]["f1"] and resposta['f2'] > swarm[i]["f2"] and resposta["f3"] < swarm[i]["f3"]:
            pBest[i] = list(swarm[i]["posicoes"]) # Copia a posição atual para pBest
            swarm[i]["f1"] = resposta['f1']
            swarm[i]["f2"] = resposta['f2']
            swarm[i]["f3"] = resposta['f3']
        # Se não domina, mas também não é dominada pelo pBest anterior, pode ser aceita com alguma probabilidade
        elif not (swarm[i]["f1"] < resposta['f1'] and swarm[i]["f2"] > resposta['f2'] and swarm[i]["f3"] < resposta['f3']):
            if random.choice([True, False]): # 50% de chance de aceitar a nova posição se não for dominada
                pBest[i] = list(swarm[i]["posicoes"])
                swarm[i]["f1"] = resposta['f1']
                swarm[i]["f2"] = resposta['f2']
                swarm[i]["f3"] = resposta['f3']

    # Atualiza o conjunto Pareto após todas as partículas terem se movido
    atualiza_pareto_set(swarm, pareto)

    # Atualiza gBest: Escolhe uma solução do conjunto de Pareto
    # Aqui, você pode usar a crowding distance para selecionar um gBest mais diversificado
    if pareto:
        fitness_keys_for_crowding = ['f1', 'f2', 'f3']
        crowding_distances = calculate_crowding_distance(pareto, fitness_keys_for_crowding)
        
        # Seleciona uma solução do Pareto com maior crowding distance para promover diversidade
        # ou, se preferir explorar, pode escolher aleatoriamente, como já estava.
        # Uma estratégia comum é selecionar aleatoriamente entre as soluções com maior crowding distance.
        max_crowding_dist = -1.0
        best_gBest_candidates = []

        for idx, dist in enumerate(crowding_distances):
            if dist == float('inf'): # Prioriza soluções nas bordas
                best_gBest_candidates.append(pareto[idx])
            elif dist > max_crowding_dist:
                max_crowding_dist = dist
                best_gBest_candidates = [pareto[idx]]
            elif dist == max_crowding_dist:
                best_gBest_candidates.append(pareto[idx])
        
        if best_gBest_candidates:
            gBest = random.choice(best_gBest_candidates)
        else:
            gBest = random.choice(pareto) # Fallback se algo der errado na seleção por crowding
    else:
        gBest = None # Caso o Pareto esteja vazio, o que não deve acontecer após a inicialização


        
res = []
for a in pareto:
    sub_list = []
    for b in a["posicoes"]:
        # Arredonda a posição para um inteiro antes de passar para contiguo
        # A função original usa math.ceil(particle_position[j]*NUM_OF_REGIONS)
        # Se a posição é um valor entre 0 e 1, e NUM_OF_REGIONS é 2,
        # math.ceil(0.1*2) = 1, math.ceil(0.9*2) = 2.
        # Então, arredondar para o inteiro mais próximo (0 ou 1) e depois mapear para regiões (1 ou 2)
        # parece mais consistente com o uso posterior.
        # Se 0 < b <= 0.5 -> 1
        # Se 0.5 < b <= 1.0 -> 2
        region_val = math.ceil(b * NUM_OF_REGIONS)
        sub_list.append(max(1, min(NUM_OF_REGIONS, region_val)))
    res.append(sub_list)

# Aplica a função contiguo às partições finais do conjunto Pareto
final_regionalizations = []
for r_list in res:
    final_regionalizations.append(contiguo(municipalities, mun_list, r_list))


nome_arquivo = "saida.txt"

with open(nome_arquivo,"w") as f:
    for sublista in final_regionalizations:
        f.write(",".join(map(str, sublista)) + "\n")
print(f"Dados salvos em '{nome_arquivo}'")

#func_1(municipalities, mun_list, [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 2, 1, 2, 2])

# Para visualização das regionalizações finais (opcional)
# for i in final_regionalizations:
#     base = plotRegionalization(stateMap, i, showCentroids=False, showBoundary=True)
#     plt.show()
#a resposta não está correta, devo procurar o que está causando o erro
#Não Apagar
#regionalization = [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1]
#base = plotRegionalization(stateMap, regionalization, showCentroids=False, showBoundary=True)