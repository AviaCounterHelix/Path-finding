from enum import Enum
import numpy as np
import open3d as o3d
#__________________________________________________________
# Перечисляемый тип узлов октодерева: 
# FREE - узел полностью свободный (нет пересечения с препяствием)
# OCCUPIED - узел полностью занят (пересекается с препятствием и достиг минимального размера)
# MIXED - узел содержит и свободное, и занятое пространство (будет разбит на детей)
#__________________________________________________________

class NodeState(Enum): 
    FREE = 0
    OCCUPIED = 1
    MIXED = 2
#__________________________________________________________
# Инициализация:
# Противоположные углы куба AABB
# Стаутс узла
# Список детей
#__________________________________________________________
class OctreeNode:
    def __init__(self, bounds_min, bounds_max):
        self.min = bounds_min # [xmin, ymin, zmin] Min координаты куба
        self.max = bounds_max # [xmax, ymax, zmax] Max координаты куба
        self.state = NodeState.MIXED # По умолчанию узел - MIXED
        self.children = [] # список из 8 дочерних узлов

#__________________________________________________________
# Пересечение узла и препятствия:
# node_min = [xmin, ymin, zmin] узла
# node_max = [xmax, ymax, zmax] узла
# Аналогично с obs - это obstacle - препятствие
# Условие проверятся по осям X,Y,Z. True при выполнении трех (шести) условий. Пересечение по трем осям.
    def intersects(self, node_min, node_max, obs_min, obs_max):
        return (node_min[0] < obs_max[0] and node_max[0] > obs_min[0] and
                node_min[1] < obs_max[1] and node_max[1] > obs_min[1] and
                node_min[2] < obs_max[2] and node_max[2] > obs_min[2])
    
#__________________________________________________________
#Исходный куб разбивается на 8 кубов. Каждый из 8 новых кубов становится дочерним узлом.
#
#        Z
#        |
#        +---+---+
#       /   /   /|
#      +---+---+ |
#      |   |   | +
#      |   |   |/
#      +---+---+
#     /
#    Y
#   /
#  X
# Вычисляем центр узла
# Тройной цикл 2*2*2 = 8 новых узлов
# Для min по осям - сх, для старта с сх - max по осям


    def split_node(self):
        cx = (self.min[0] + self.max[0]) / 2.0 # X центра узла
        cy = (self.min[1] + self.max[1]) / 2.0 # Y центра узла
        cz = (self.min[2] + self.max[2]) / 2.0 # Z центра узла
        children = []
        
        for x in [self.min[0], cx]:
            for y in [self.min[1], cy]:
                for z in [self.min[2], cz]:
                    child_min = [x, y, z]
                    child_max = [
                        cx if x == self.min[0] else self.max[0],
                        cy if y == self.min[1] else self.max[1],
                        cz if z == self.min[2] else self.max[2]
                    ]
                    children.append(OctreeNode(child_min, child_max)) # Создание нового octree
        return children
#__________________________________________________________
# Рекурсия на построение дерева:
# Базовый сценарий - размер узла = min размеру (30 мм)

    def subdivide(self, obstacles, min_size=30.0):
        size = self.max[0] - self.min[0] # Размер определеям по 1-й оси так как работаем с кубами

        if size <= min_size: # Если размер меньше или равне минимального, то делить узел уже нельзя
            self.state = NodeState.OCCUPIED if any(
                self.intersects(self.min, self.max, obs[0], obs[1]) for obs in obstacles
            ) else NodeState.FREE
            return # Определяем только статус узла, свободен или занят, далее остановка

        if not any(self.intersects(self.min, self.max, obs[0], obs[1]) for obs in obstacles):
            self.state = NodeState.FREE
            return # если узел имеет размер больше минимального, но свободен, то тоже остановка

        self.children = self.split_node() # Иначе делим узел на 8 частей, так как он пересекается с препятствием - MIXED
        self.state = NodeState.MIXED

        for child in self.children: # Вызов рекурсии на обработку 8 новых узлов
            child.subdivide(obstacles, min_size)        
#__________________________________________________________          

# Границы пространства и минимальный размер 
SPACE_BOUNDS = np.array([[0.0, 0.0, 0.0], [1000.0, 500.0, 500.0]])
MIN_SIZE = 30.0

# Исходные точки препятствий
obstacles_points = [
    np.array([[174.89,136,38.71], [174.89,136,138.71], [274.89,136,138.71], [274.89,136,38.71],
              [174.89,236,38.71], [174.89,236,138.71], [274.89,236,138.71], [274.89,236,38.71]]),
    np.array([[174.89,61,288.71], [174.89,61,388.71], [274.89,61,388.71], [274.89,61,288.71],
              [174.89,161,288.71], [174.89,161,388.71], [274.89,161,388.71], [274.89,161,288.71]]),
    np.array([[460,227.99,173.28], [460,227.99,273.28], [560,227.99,273.28], [560,227.99,173.28],
              [460,327.99,173.28], [460,327.99,273.28], [560,327.99,273.28], [560,327.99,173.28]]),
    np.array([[460,183.99,398.28], [460,183.99,498.28], [560,183.99,498.28], [560,183.99,398.28],
              [460,283.99,398.28], [460,283.99,498.28], [560,283.99,498.28], [560,283.99,398.28]]),
    np.array([[674.89,61,288.71], [674.89,61,388.71], [774.89,61,388.71], [774.89,61,288.71],
              [674.89,161,288.71], [674.89,161,388.71], [774.89,161,388.71], [774.89,161,288.71]]),
    np.array([[865.98,275.15,60.24], [865.98,275.15,160.24], [965.98,275.15,160.24], [965.98,275.15,60.24],
              [865.98,375.15,60.24], [865.98,375.15,160.24], [965.98,375.15,160.24], [965.98,375.15,60.24]])
]

#__________________________________________________________          
# Подготовка AABB: вычисляем min/max один раз до рекурсии
# Получаем numpy массив препятствий ([x1min, y1min, z1min], [x1max, y1max, z1max]...[n=6])
obstacles_aabb = [(obs.min(axis=0).tolist(), obs.max(axis=0).tolist()) for obs in obstacles_points]

#__________________________________________________________ 
# Создание корневого узла
root = OctreeNode(SPACE_BOUNDS[0].tolist(), SPACE_BOUNDS[1].tolist()) # Охватывает все пространство

#__________________________________________________________ 
# Запуск построения дерева
root.subdivide(obstacles_aabb, MIN_SIZE)

print('Octree построен успешно')

#__________________________________________________________          
# Визуализируем только листы

def collect_nodes(node, points, lines, colors, index_map):
    if not node.children: # Проверка на детей
        x_min, y_min, z_min = node.min
        x_max, y_max, z_max = node.max

        corners = [
            (x_min, y_min, z_min), (x_max, y_min, z_min),
            (x_min, y_max, z_min), (x_max, y_max, z_min),
            (x_min, y_min, z_max), (x_max, y_min, z_max),
            (x_min, y_max, z_max), (x_max, y_max, z_max)
        ] # Массив координат для отрисовки листа

        corner_indices = [] # Дедупликация вершин
        for pt in corners:
            if pt not in index_map:
                index_map[pt] = len(points)
                points.append(pt)
            corner_indices.append(index_map[pt])

        edges = [(0,1), (2,3), (4,5), (6,7), # 12 ребер куба
                 (0,2), (1,3), (4,6), (5,7),
                 (0,4), (1,5), (2,6), (3,7)]

        if node.state == NodeState.OCCUPIED:
            color = [0.9, 0.2, 0.2]      # красный для занятых
        elif node.state == NodeState.MIXED:
            color = [0.8, 0.8, 0.2]      # жёлтый (не встречается для листов)
        else:
            color = [0.6, 0.6, 0.6]      # серый для свободных

        for i, j in edges:
            lines.append([corner_indices[i], corner_indices[j]]) # Добавляем отрезок и его цвет в lines
            colors.append(color)
    else:
        # Внутренний узел – просто идём глубже, не рисуя его каркас
        for child in node.children:
            collect_nodes(child, points, lines, colors, index_map)
#__________________________________________________________

# Вызов функции 
points = []
lines = []
colors = []
index_map = {}
collect_nodes(root, points, lines, colors, index_map)

#__________________________________________________________
# Создание  LineSet
line_set = o3d.geometry.LineSet()
line_set.points = o3d.utility.Vector3dVector(points)
line_set.lines = o3d.utility.Vector2iVector(lines)
line_set.colors = o3d.utility.Vector3dVector(colors)

#__________________________________________________________
# Каркас пространства
space_box = o3d.geometry.AxisAlignedBoundingBox(SPACE_BOUNDS[0], SPACE_BOUNDS[1])
space_box.color = [0, 0, 0]

#__________________________________________________________
o3d.visualization.draw_geometries(
    [line_set, space_box], 
    window_name="Octree: Red=Occupied, Yellow=Mixed, Gray=Free"
)