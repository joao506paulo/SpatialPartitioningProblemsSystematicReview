from utils import workWithStateData, add_medical_procedures, isFeasible, computeDistanceMatrix, dominance_ranking, calculate_crowding_distance, crowded_binary_tournament
import gurobipy as gp
from gurobipy import GRB

### Load state data
#Roraima state
#file_state_data = "../data/State_Roraima/Municipios_RR.xlsx"
#nrows_file_state_data = 168
#file_state_map_json = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.json"
#object_name = "RR_Municipios_2022"
#file_state_map_shapefile = "../data/State_Roraima/RR_Municipios_2022/RR_Municipios_2022.shp"

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
#lista para teste
partition_list = [0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]
print(distances)

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
        soma_i = soma_i - H
        if soma_i < 0:
            soma_i = soma_i* (-1)
        soma_l += soma_i
 
    f1 = soma_l / NUM_OF_REGIONS
    #print(f1)
    return f1

#func_1(municipalities, mun_list, partition_list)


#tentativa errada
def func_3l (municipalities, mun_list, partition_list):
    soma_l = 0
    mim = 1000000
    for l in range(NUM_OF_REGIONS):
        soma_i = 0
        for i in range(NUM_UNITS):
            for j in municipalities[mun_list[i]]:
                if partition_list[i] == l and partition_list[mun_list.index(j)] == l: #esse j está errado, ver como conseguir o certo
                    result = menor_dist(municipalities, mun_list, partition_list, i)
                    if result < mim:
                        mim = result
            soma_i+= mim

        soma_l += soma_i

    f2 = soma_l
    #print(f2)
    return f2

def menor_dist (municipalities, mun_list, partition_list, n_municipio):
    n = 1000000
    conta = 0

    for i in municipalities[mun_list[n_municipio]]['vizinhos']:
        #print(municipalities[mun_list[n_municipio]])
        #como definir Yij e Yjl ou verificar se os dois municípios estão na mesma região?
        conta = municipalities[mun_list[n_municipio]]['NUM_HABITANTES']*municipalities[mun_list[n_municipio]]['vizinhos'][i]['dist_linha']#*(1-Yij)Yjl#desnecessário
        if conta < n:    
            n = conta
    return n

def func_2 (municipalities, mun_list, partition_list):
    #acessar os procedimentos médicos de cada município  
    procedimentos = set()
    soma_l = 0
    for l in range(NUM_OF_REGIONS):
        procedimentos.clear()
        for i in range(NUM_UNITS):
            if partition_list[i] == l:
                for procedimento in municipalities[mun_list[i]]['procedimentos']: #preciso ver como adicionar os procedimentos de cada municício ao municipalities
                    procedimentos.add(procedimento)
        soma_l += len(procedimentos)
        
    f2 = soma_l / NUM_OF_REGIONS
    
    return f2  

def func_3 (municipalities, mun_list, partition_list):
    soma_l = 0
    for l in range(NUM_OF_REGIONS):
        soma_i = 0
        for i in range(NUM_UNITS):
            mim = float("inf")
            soma = False
            for j in range (NUM_UNITS):
                if partition_list[i] != l and partition_list[j] == l:
                    dist = distances[(mun_list[i],mun_list[j])]
                    result = municipalities[mun_list[i]]['NUM_HABITANTES'] * dist
                    #print(result)
                    if result < mim: 
                        mim = result
                        soma = True
                        #print(mim)    
            if soma:
                soma_i += mim
        soma_l += soma_i
    f3 = soma_l
    return f3    

def funcoes_objetivo (municipalities, mun_list, partition_list):
    resposta = {}
    resposta['f1'] = func_1(municipalities, mun_list, partition_list)
    resposta['f2'] = func_2(municipalities, mun_list, partition_list)
    resposta['f3'] = func_3(municipalities, mun_list, partition_list)
    return resposta
         
                    


#print(func_1(municipalities, mun_list, [2,2,1,2,2,2,2,2,2,1,2,2,2,2,2]))
#print(func_1(municipalities, mun_list, [1,1,2,1,1,1,1,1,1,1,1,1,1,1,1]))

#print(func_1(municipalities, mun_list, [2,2,2,0,0,0,0,0,0,0,2,0,0,0,0]))
#print(func_2(municipalities, mun_list, [2,2,2,0,0,0,0,0,0,0,2,0,0,0,0]))
#print(func_3(municipalities, mun_list, [2,2,2,0,0,0,0,0,0,0,2,0,0,0,0]))
