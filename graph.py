
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

class Node():
    def __init__(self, name):
        self.name = name
        self.parent_nodes = []
        self.child_nodes = []
        self.lower_nodes = []
        self.higher_nodes = None
        self.pos = False

    def add_child(self, obj):
        self.child_nodes.append(obj)
    
    def add_parent(self, obj):
        self.parent_nodes.append(obj)

    def add_lower(self, obj):
        self.lower_nodes.append(obj)

    def add_higher(self, obj):
        self.higher_nodes.append(obj)

    def remove_child(self, obj):
        self.child_nodes.remove(obj)
    
    def remove_parent(self, obj):
        self.parent_nodes.remove(obj)
    
    def remove_lower(self, obj):
        self.lower_nodes.remove(obj)
    
    def remove_higher(self, obj):
        self.higher_nodes.remove(obj)

    def empty_childs(self):
        self.child_nodes = []

    def empty_lowers(self):
        self.lower_nodes = []

    def empty_highers(self):
        self.higher_nodes = []

    def get_childs(self):
        return self.child_nodes
    
    def get_parents(self):
        return self.parent_nodes
    
    def get_lowers(self):
        return self.lower_nodes
    
    def get_highers(self):
        return self.higher_nodes

    def num_childs(self):
        return len(self.child_nodes)

    def num_lowers(self):
        return len(self.lower_nodes)

    def num_highers(self):
        return len(self.higher_nodes)

    def is_leaf(self):
        return len(self.child_nodes) == 0
    
    def can_reach(self, node, visited=[]):
        if len(visited) == 0:
            for lower in self.lower_nodes:
                if lower != node:
                    visited.append(lower)
                    if lower.can_reach(node, visited):
                        return True
        else:
            for child in self.child_nodes:
                if child not in visited:
                    if child == node:
                        return True
                    else:
                        visited.append(child)
                        if child.can_reach(node, visited):
                            return True
        return False

    def __str__(self):
        return self.name

class Graph():
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
    
    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return False

    def is_empty(self):
        return len(self.nodes) == 0

    def get_node_list(self, func=lambda x : x.num_lowers()):
        self.nodes = sorted(self.nodes, key=func)
        return self.nodes