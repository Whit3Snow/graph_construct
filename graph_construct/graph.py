
# 다중 트리(And-or 그래프)에 필요한 함수들 
"""
1. insert 함수 (각각 parent, child 화살표 추가하는 함수) 
2. delete 함수?
3. 탐색 함수(화살표 방향을 어떻게 할지 고민중임 --> Andor 그래프랑 똑같이 하기로 결정함)
4. End 노드 따로 만들기 (data 값 : END)

3. 그래프가 해야 할 task...
    하나의 노드를 했으면 다음 노드로 이동
    하나의 노드를 마친다는 것은 그것의 자식 노드들이 모두 이루어졌을 경우에만 해당.
    --> # 문제점: 하는 과정 속에서 이를 어떻게 complete 한 것인지 알 수 있는가? #

    만약 부모가 여러 명인 경우 하나만 해도 그 부모 노드로 이동할 수 있다.

    End node에 도착을 하면 print("sucess") 


노드에 들어갈 것 
- action 값
- parent : 부모 노드들(노드 리스트)
- child : 자식 노드들(자식 리스트)
- conf : action 완료
- num : 단계
- end : end node 인지 알려줌 
"""

class Snode():
    def __init__(self, action, num, end):
        self.action = action
        self.num = num
        self.conf = False
        self.parent = []
        self.child = [] 
        
        if end:
            self.end = end
        else:
            self.end = False

    
    def c_add(self, obj):
        self.child.append(obj)
    
    def p_add(self, obj):
        self.parent.append(obj)


# class Sgraph():
#     def __init__(self, end):
#         self.end = end
    
#     def research(self, value):
        
# 시작을 어떻게 해야할지 모르겠어요...
# 
# def research():

    