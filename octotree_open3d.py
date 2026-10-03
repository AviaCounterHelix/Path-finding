from enum import Enum
import numpy as np
import open3d as o3d
from scipy.spatial import KDTree
import heapq

#__________________________________________________________
# Перечисляемый тип узлов октодерева: 
# FREE - узел полностью свободный - нет пересечения с препяствием
# OCCUPIED - узел полностью занят - пересекается с препятствием или достиг минимального размера
# MIXED - узел содержит и свободное, и занятое пространство - будет разбит на детей (8 узлов)
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
        self.min = bounds_min # [xmin, ymin, zmin] Min координаты куба - левый нижний ближний угол
        self.max = bounds_max # [xmax, ymax, zmax] Max координаты куба - правый верхний дальний угол
        self.state = NodeState.MIXED # По умолчанию узел - MIXED
        self.children = [] # список из 8 дочерних узлов. Если список пуст - то это лист, далее не делить

#__________________________________________________________
# Проверка пересечение узла и препятствия:
# node_min = [xmin, ymin, zmin] узла
# node_max = [xmax, ymax, zmax] узла
# Аналогично с obs - это obstacle - препятствие
# Условие проверятся по осям X,Y,Z. True при выполнении шести условий. Пересечение по трем осям.
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
        children = [] # cписок для дочерних узлов
        
        for x in [self.min[0], cx]:
            for y in [self.min[1], cy]:
                for z in [self.min[2], cz]:
                    child_min = [x, y, z]
                    child_max = [
                        cx if x == self.min[0] else self.max[0],
                        cy if y == self.min[1] else self.max[1],
                        cz if z == self.min[2] else self.max[2]
                    ]
                    children.append(OctreeNode(child_min, child_max)) # Создание нового узла
        return children
#__________________________________________________________
# Рекурсия на построение дерева:
# Базовый сценарий - размер узла = min размеру (30 мм)
# Дерево рекурсии 
#
# root (1000 мм, MIXED)
#├── child1 (500 мм, проверяется)
#│   ├── если свободен → FREE, стоп
#│   ├── если пересекает → делится на 8 детей по 250 мм
#│   │   └── ... рекурсия ...
#│   └── если размер ≤ 30 → FREE или OCCUPIED, стоп
#├── child2 (500 мм, проверяется)
#│   └── ...
#└── ... (8 детей)
#__________________________________________________________

    def subdivide(self, obstacles, min_size=30.0):
        size = self.max[0] - self.min[0] # Размер определеям по 1-й оси так как работаем с кубами

        if size <= min_size: # Если размер меньше или равен минимальному, то делить узел уже нельзя
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

# Границы пространства и минимальный размер куба
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
# Запуск рекурсивного построения дерева
root.subdivide(obstacles_aabb, MIN_SIZE)

print('Octree построен успешно')

#__________________________________________________________          
# Визуализируем только листы

def collect_nodes(node, points, lines, colors, index_map):
    if not node.children: # Проверка на детей. Если детей нет - это лист. Его визуализируем.
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
        # Если узел имеет детей - идем глубже, не рисуем его каркас
        for child in node.children:
            collect_nodes(child, points, lines, colors, index_map)

#__________________________________________________________
            
#Вершины:                    Рёбра:
#    6────────7              Горизонтальные (нижние): (0,1), (2,3)
#   /│       /│              Горизонтальные (верхние): (4,5), (6,7)
#  4────────5 │              Горизонтальные (боковые): (0,2), (1,3)
#  │ │      │ │              Вертикальные: (0,4), (1,5), (2,6), (3,7)
#  │ 2──────│─3              Диагональные (нет, только рёбра куба)
#  │/       │/
#  0────────1            
#__________________________________________________________

# Вызов функции 
points = [] # список для накопления вершин
lines = [] # Список для накопления ребер
colors = [] # Список для накопления цвета ребер
index_map = {} # Словарь для депупликации вершин
collect_nodes(root, points, lines, colors, index_map)

#__________________________________________________________
# Создание  LineSet
line_set = o3d.geometry.LineSet() # Контейнер Open3D
line_set.points = o3d.utility.Vector3dVector(points) # Преобразование в формат Open3D
line_set.lines = o3d.utility.Vector2iVector(lines) # Преобразование в формат Open3D
line_set.colors = o3d.utility.Vector3dVector(colors) # Преобразование в формат Open3D

#__________________________________________________________
# Каркас пространства
space_box = o3d.geometry.AxisAlignedBoundingBox(SPACE_BOUNDS[0], SPACE_BOUNDS[1]) # Создание базового параллелепипеда
space_box.color = [0, 0, 0]

#__________________________________________________________

# Сбор свободных листьев
free_leaves = [] # Список свободных листьев

def collect_free_leaves(node):
    if not node.children:  # проверка узла является ли он листом (лист нельзя разделить)
        if node.state == NodeState.FREE: # проверка является ли лист свободным
            center = [
                (node.min[0] + node.max[0]) / 2, # вычисление центра листа - куба. Это точки будут использованы в А*
                (node.min[1] + node.max[1]) / 2,
                (node.min[2] + node.max[2]) / 2
            ]
            size = node.max[0] - node.min[0] # вычисляем характерный размер куба
            
            free_leaves.append({            # список со словарями: лист + его атрибуты
                'center': np.array(center),
                'size': size,
                'min': np.array(node.min), # не используем
                'max': np.array(node.max), # не используем
                'node': node  # ссылка на исходный узел
            })
    else:
        for child in node.children: # если узел не является листом, то рекурсино обходим всех детей
            collect_free_leaves(child)

# Запуск сбора свободных листьев от корня
collect_free_leaves(root)

#__________________________________________________________
# Создаём массив центров для KDTree 

centers_array = np.array([leaf['center'] for leaf in free_leaves]) # массив координат свободных листьев (N, 3) [x, y, z]

print(f"Форма массива: {centers_array.shape}")
print(f"Первые 3 центра:\n{centers_array[:3]}")

sizes_array = np.array([leaf['size'] for leaf in free_leaves]) # массив размеров свободных листьев (N,) [size]

print(f"Максимальный размер листа: {sizes_array.max()}")
print(f"Минимальный размер листа: {sizes_array.min()}")

# Строим KDTree на основе центров листьев
tree = KDTree(centers_array)

# Радиус поиска
radius = sizes_array.max() * 1.5 # радиус для поиска соседей по дереву

# Находим всех соседей на основе радиуса поиска
pairs = tree.query_pairs(radius)

print(f"Найдено пар кандидатов: {len(pairs)}")

# Фильтрация реальных соседей___________________

print(f"Фильтрация {len(pairs)} пар")
real_neighbors = [] # список для хранения индексов реальных соседей
half_sizes = sizes_array / 2.0

# Проходим по парам
for i, j in pairs:
    # Эвклидово расстояние между центрами кубов
    dist = np.linalg.norm(centers_array[i] - centers_array[j])
    
    # Ожидаемое расстояние: сумма полу-размеров
    expected_dist = half_sizes[i] + half_sizes[j]
    
    # Допуск = 60% от размера меньшего куба
    tolerance = min(half_sizes[i], half_sizes[j]) * 0.6
    
    # Определение реальных соседей: если реальное расстояние - ожидаемое <= допуску
    if abs(dist - expected_dist) <= tolerance:
        real_neighbors.append((i,j))
        
print(f"Связей после фильтрации: {len(real_neighbors)}")

# Построение словаря смежности: ключ - это индекс узла, значение - список индексов его соседей. 
adjacency = {i: [] for i in range(len(centers_array))}

for i,j in real_neighbors: # перебор пар и определение двухстороенней связи из i в j, а также из j в i
    adjacency[i].append(j)
    adjacency[j].append(i)
    
print(f"Список смежности: {len(adjacency)} узлов")


# Поиск пути А*___________________

start_point = np.array([90.0, 316.77, 40.55]) # стартовая точка
goal_point = np.array([830, 205.21, 390.0])  # финальная точка

# Находим ближайшие узлы к точкам через KDTree
_, start_idx = tree.query(start_point)
_, goal_idx = tree.query(goal_point)

print(f"Старт: {start_point} - узел {start_idx}")
print(f"Финиш: {goal_point} - узел {goal_idx}")

# Функция А*___________________

def a_star(start_idx, goal_idx, adjacency, centers_array):
    if start_idx == goal_idx: # проверка на совпадение старта и финиша
        return [start_idx]

    open_set = [] # список для хранения f_score и node_index. Минимальный f_score на "вершине"
    heapq.heappush(open_set, (0.0, start_idx)) # Стартовый узел имеет f_score = 0.0

    came_from = {} # Словарь для восстановления пути, ключ - индекс узла, значение - индекс узла, из которого мы пришли
    g_score = {start_idx: 0.0} # Словарь стоимости пути до каждого узла: 0 - для стартового узла, бесконечность - для остальных
    closed_set = set() # Сет для уже обработанных узлов
    goal_center = centers_array[goal_idx] # Координаты целевеого узла - финищ пути

    while open_set: # Обработка всей очереди
        _, current = heapq.heappop(open_set) # извлечение узла с наименьшим f_score

        if current == goal_idx: # если нашли путь (финишную точку)
            path = [] # создаем пустой список
            while current in came_from: # начинаем с целевого узла и идем обратно, стартовый узел не включен в came_from
                path.append(current)
                current = came_from[current]
            path.append(start_idx) # включаем стартовый узел
            path.reverse() # разворачиваем путь от старта к цели-финишу
            return path

        if current in closed_set: # если узел уже был обработан, то пропускаем его
            continue
        closed_set.add(current) # пометка узла, что он обрабтан

        for neighbor in adjacency[current]: # перебираем всех соседей из списка смежности
            if neighbor in closed_set: # пропускаем, если узел уже обработан
                continue

            # Вычисление стоимости перехода к соседнему узлу
            edge_cost = np.linalg.norm(
                centers_array[current] - centers_array[neighbor]) # Евклидово расстояние между центрами кубов

            tentative_g = g_score[current] + edge_cost # пробная стоимость пути от старта до соседа через текущий узел

            if tentative_g < g_score.get(neighbor, float('inf')): # проверка, является ли найденный путь к соседу лучше ранее известного
                came_from[neighbor] = current # лучший путь до соседа через текущий узел
                g_score[neighbor] = tentative_g # обновление стоимости пути до соседа

                # Эвристика: эвклидово расстояние от соседа до цели
                h_score = np.linalg.norm(
                    centers_array[neighbor] - goal_center)

                f_score = tentative_g + h_score # вычисление приоритета узла, чем меньше f_score, тем выше приоритет
                heapq.heappush(open_set, (f_score, neighbor)) # добавление соседа в очередь с приоритетом

    return []  # если путь не найден

#__________________________
# Формула A:*
# f(n) = g(n) + h(n)

# где:
#  f(n) — общая стоимость пути через узел n
#  g(n) — реальная стоимость от старта до n
#  h(n) — эвристическая оценка стоимости от n до цели
#__________________________

# Запуск поиска__________________________

path_indices = a_star(start_idx, goal_idx, adjacency, centers_array)

if path_indices: # проверка что список не пуст
    path_points = centers_array[path_indices] # извлекает центры кубов по пути
    total_dist = sum(
        np.linalg.norm(path_points[i+1] - path_points[i])
        for i in range(len(path_points)-1))  # вычисление длины пути
    print("Путь найден!")
    print(f"Узлов в пути: {len(path_indices)}")
    print(f"Длина пути: {total_dist:.1f} мм")

#__________________________
   
# Визуализация пути в open3D_______________

    # линия пути - зеленая 
    path_lines = [[i, i + 1] for i in range(len(path_points) - 1)] # создание линий пути от точке к точке
    path_colors = [[0.0, 0.9, 0.0] for _ in path_lines]  # зелёный цвет для всех линий пути

    path_line_set = o3d.geometry.LineSet() # объект LineSet для отрисовки пути
    path_line_set.points = o3d.utility.Vector3dVector(path_points) # точки пути
    path_line_set.lines = o3d.utility.Vector2iVector(path_lines) # линии пути
    path_line_set.colors = o3d.utility.Vector3dVector(path_colors) # цвет линий

    # точка старта - синяя сфера
    start_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=8.0, resolution=16) # сфера радиусом 8 мм
    start_sphere.translate(start_point)
    start_sphere.paint_uniform_color([0.1, 0.3, 0.9])  # синий цвет

    # точка цели - жёлтая сфера
    goal_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=8.0, resolution=16) # сфера радиусом 8 мм
    goal_sphere.translate(goal_point)
    goal_sphere.paint_uniform_color([0.9, 0.8, 0.1])  # жёлтый цвет

    # запуск визуализации
    o3d.visualization.draw_geometries(
        [line_set, space_box, path_line_set, start_sphere, goal_sphere],
        window_name="A* Path: Green=Path, Blue=Start, Yellow=Goal")
    
    # печать координат точек пути
    print("\n📍 Координаты точек пути:")
    for i, point in enumerate(path_points):
        print(f"   Узел {i:2d}: X={point[0]:7.2f}  Y={point[1]:7.2f}  Z={point[2]:7.2f}")
else:
    print("Путь не найден!")
