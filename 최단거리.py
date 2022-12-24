#0. 기초 변수 설정
import random
import itertools

startNode = "E" #출발 지점
INF = int(2e9) # 2의 109승. 

nodeList = ["A",'B','C','D','E','F'] #각 쓰레기통 지점
node_connection = [#각 지점과 서로 연결된 지점 
    ['B','D'],
    ['A','C','E'],
    ["B","F"],
    ["A","E"],
    ["B","D","F"],
    ["C","E"]
]

edge_length = { #연결된 지점 간 거리(임의 지정)
    frozenset(("A","B")) : 4,
    frozenset(("A","D")) : 5,
    frozenset(("B",'C')) : 7,
    frozenset(('B','E')) : 3,
    frozenset(("C",'F')) : 6,
    frozenset(("D",'E')) : 9,
    frozenset(('E','F')) : 3
    }

station_to_E = 5 #쓰레기 수거장에서 E까지의 거리
wastebin_speed = [5,2,4,3,2,3] #A ~ F의 하루 당 쓰레기 축적량 (random 함수 이용할 것임.)


#1. 쓰레기통까지의 최단 경로 찾기 - 다익스트라 알고리즘 (시간 복잡도: O(n^2))


def get_lowest_node(v, d): #시작지점부터 최단거리면서 방문하지 않은 쓰레기통 출력 v = visited, d = distance_from_start
    ret = 0
    minimum_length = INF
    for i in range(6):
        if (not v[i]) and d[i] < minimum_length:
            minimum_length = d[i]
            ret = i
    return ret

def FindMinPath(start, end):
    visited = [False] * 6 #방문 체크
    distance_from_start = [INF] * 6 #시작지점부터 A~F까지의 경로를 설정.
    visited[start] = True
    for i in range(6):
        if nodeList[i] in node_connection[start]:
            distance_from_start[i] = edge_length[frozenset((nodeList[i], nodeList[start]))] #인접 쓰레기통일 경우 거리를 넣음
        elif i == start:
            distance_from_start[i]=0
        else:
            continue
    for k in range(6):
        current_node = get_lowest_node(visited, distance_from_start)#시작지점부터 최단 거리의 인접지점 (index)
        visited[current_node] = True
        for j in node_connection[current_node]:
            cost = distance_from_start[current_node] + edge_length[frozenset((j, nodeList[current_node]))] #ex: A(시작) --> B(CURRENT NODE) --> C(B에 인접한 쓰레기통)의 거리
            if cost < distance_from_start[nodeList.index(j)]:
                distance_from_start[nodeList.index(j)] = cost

       
    return distance_from_start[end]

#2. 쓰레기 설정
#쓰레기통: 20을 한계량으로 설정. 20 초과 시 쓰레기가 제대로 수거되지 않은 것으로 간주, 추후 페널티 부여


variation_float = 0.5 #쓰레기의 변동 편차
def randomize_trash(n):
    return round(random.uniform(float(n-variation_float), float(n + variation_float)), 3)

def fill_trash(wasteList):
    for i in range(len(wasteList)):
        wasteList[i] += randomize_trash(wastebin_speed[i])

#3. 실험군: 스마트 쓰레기통을 적극 활용한 방법 : 쓰레기의 양이 16 이상일 경우 쓰레기차 파견. 이때, 쓰레기차의 크기를 줄인다 가정
Exp_group = {
    'wastebin_exp' : [0] * len(nodeList),
    'gas_milage_exp' : 1,
    'movement_cost' : 0,
    'day' : 0,
    'trash_got' : 0
}

def day_pass_exp():
    Exp_group['day'] += 1
    fill_trash(Exp_group["wastebin_exp"]) #매일 쓰레기를 채움
    node_went = []#출력용. 수거하러 간 쓰레기통의 위치 표시
    for i in range(len(nodeList)):
        if Exp_group['wastebin_exp'][i] >= 16: #쓰레기 양이 16보다 크면
            node_went.append(nodeList[i]) #다녀온 쓰레기통 위치 추가 --> 쓰레기통의 이름으로 추가됨
    
    if len(node_went) > 1:
        possible_permut = list(itertools.permutations(node_went)) #지나가는 모든 순서 조합 설정 --> 최솟값 구하는데 이용함. return: 튜플 ex: a, b --> (a, b) (b, a)
        min_value = INF
        for i in range(len(possible_permut)):
            foo = FindMinPath(4, nodeList.index(possible_permut[i][0])) + 5
            for j in range(len(node_went)- 1):
                foo += FindMinPath(nodeList.index(possible_permut[i][j]),nodeList.index(possible_permut[i][j+1]))
            foo += FindMinPath(nodeList.index(possible_permut[i][-1]), 4) + 5
            min_value = min(min_value, foo)
            
        
        if min_value != INF:
            Exp_group['movement_cost'] += min_value
            print('이동거리:', min_value)
        else:
            print('err')
    if len(node_went) == 1:
        Exp_group['movement_cost'] += FindMinPath(4, nodeList.index(node_went[0]))
    for k in node_went:
        Exp_group['trash_got'] += Exp_group['wastebin_exp'][nodeList.index(k)] 
        Exp_group['wastebin_exp'][nodeList.index(k)] = 0
    

        

    print(f"Day {Exp_group['day']}\n\n수거하러 간 쓰레기통 : {node_went}\n총 이동 비용 : {Exp_group['movement_cost']}\n총 수거량 : {Exp_group['trash_got']}\n쓰레기 현황 : {Exp_group['wastebin_exp']}")




#4. 대조군 : 기존의 수거 방식. 다수의 쓰레기를 운반하므로 더 연비가 낮으며, 일정한 운행 기간 동안 운행함. 쓰레기의 과적량 발생 시 운행 빈도를 줄임

Ctrl_group = {
    'wastebin_ctrl' : [0] * len(nodeList),
    'gas_milage_ctrl' : 1.5, #이 부분은 조정 가능. 연비는 실험군의 1.5배로 생각하였음.
    'movement_cost' : 0,
    'day' : 0,
    'trash_got' : 0,
    'cycle' : 5, #5일마다 한 번씩 돌겠다는 의미.
    'prev_day' : 0,
    'next_day' : 5 
}



def day_pass_ctrl():

    #이전 운행 날과, 차후 운행 날. cycle의 변동에 의해 조정되는 것을 감안하기 위해 % 대신 생각. 첫날 운행을 위해 1로 조정
    Ctrl_group['day'] += 1
    fill_trash(Ctrl_group["wastebin_ctrl"]) #매일 쓰레기를 채움
    bin_overflow = []
    for i in range(len(Ctrl_group['wastebin_ctrl'])):
        if Ctrl_group['wastebin_ctrl'][i] > 20:
            bin_overflow.append(nodeList[i])
    if len(bin_overflow) > 0:
        print(f"쓰레기 초과가 {bin_overflow}에서 발생했습니다. 순환 날짜를 1 감소시키며, 오늘 운행을 시작합니다.")
        Ctrl_group['next_day'] = Ctrl_group['day']
        Ctrl_group['cycle'] -= 1
        bin_overflow = []

    if Ctrl_group['day'] == Ctrl_group['next_day']:
        Ctrl_group['movement_cost'] += Ctrl_group['gas_milage_ctrl'] * (2 * station_to_E + edge_length[frozenset(('E','D'))] + edge_length[frozenset(('A','D'))] + edge_length[frozenset(('A','B'))] +  edge_length[frozenset(('B','C'))] +  edge_length[frozenset(('C','F'))] + edge_length[frozenset(('E','F'))])
        for i in range(len(nodeList)):
            Ctrl_group['trash_got'] += Ctrl_group['wastebin_ctrl'][i]
            Ctrl_group['wastebin_ctrl'][i] = 0
            

        #운행 경로는 고정임. E - D - A - B - C - F -E
        Ctrl_group['prev_day'] = Ctrl_group['day']
        Ctrl_group['next_day'] += Ctrl_group['cycle']
    
    print(f"Day {Ctrl_group['day']}\n\n총 이동 비용 : {Ctrl_group['movement_cost']}\n총 수거량 : {Ctrl_group['trash_got']}\n현재 수거 주기 : {Ctrl_group['cycle']}\n쓰레기 현황: {Ctrl_group['wastebin_ctrl']}\nnext_day: {Ctrl_group['next_day']}")

    

testing = True

msg = input('실험을 선택하세요\nEXP: 실험군, CTRL: 대조군')
testmode = input('모드를 선택하세요\nA: 자동으로 100까지의 실험 진행.\nP: 직접 날짜를 넘기며 실험 진행. 아무 키를 눌러 날짜를 넘기고, stop을 쳐서 실험을 완료합니다.')
if msg == 'EXP' and testmode =='P':
    while testing:
        if input() == 'stop':
            print(f"실험 종료 : 효율 = {Exp_group['trash_got']/Exp_group['movement_cost']} ") #효율 = 쓰레기 수거량 / 연료 소비량
            testing = False    
        else:
            day_pass_exp()
elif msg == 'EXP' and testmode == 'A':
    for i in range(100):
        day_pass_exp()
    print(f"실험 종료 : 효율 = {Exp_group['trash_got']/Exp_group['movement_cost']} ") #효율 = 쓰레기 수거량 / 연료 소비량
    
elif msg == 'CTRL' and testmode == 'P':
    if input() == 'stop':
        print(f"실험 종료 : 효율 = {Ctrl_group['trash_got'] / Ctrl_group['movement_cost']} ") #효율 = 쓰레기 수거량 / 연료 소비량
        testing = False    
    else:
        day_pass_exp()
        #day_pass_ctrl()
elif msg == 'CTRL' and testmode == 'A':
    for i in range(100):
        day_pass_ctrl()
    print(f"실험 종료 : 효율 = {Ctrl_group['trash_got'] / Ctrl_group['movement_cost']} ") #효율 = 쓰레기 수거량 / 연료 소비량
        
else: print('잘못된 커맨드입니다. 다시 실행해주세요. ')