import numpy as np

def voxelize_box(A, B, C, D, resolution):
    """
    Вход:
        A, B, C, D - четыре точки (list/tuple/np.array длины 3).
                      A - общая вершина, AB, AC, AD - три смежных ребра параллелепипеда.
        resolution - число вокселей вдоль каждого ребра (целое > 0).
    Возвращает:
        список list of [x, y, z] координат центров всех вокселей.
    """
    # Преобразуем в numpy массивы
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    C = np.array(C, dtype=float)
    D = np.array(D, dtype=float)

    # Три вектора рёбер от вершины A
    u = B - A
    v = C - A
    w = D - A

    # Координаты центров вокселей внутри единичного куба [0,1)^3
    offsets = (np.arange(resolution) + 0.5) / resolution

    # Вычисляем координаты всех вокселей через broadcasting
    X = A[0] + offsets[:, None, None] * u[0] \
              + offsets[None, :, None] * v[0] \
              + offsets[None, None, :] * w[0]
    Y = A[1] + offsets[:, None, None] * u[1] \
              + offsets[None, :, None] * v[1] \
              + offsets[None, None, :] * w[1]
    Z = A[2] + offsets[:, None, None] * u[2] \
              + offsets[None, :, None] * v[2] \
              + offsets[None, None, :] * w[2]

    # Собираем в массив точек и вытягиваем в список
    points = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    return points.tolist()


import matplotlib.pyplot as plt

def visualize_voxels(points):
    """
    Отображает список точек (центров вокселей) в 3D.
    points: список [x, y, z] или numpy массив (N,3)
    """
    points = np.array(points)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Рисуем все центры вокселей маленькими точками
    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
               c='blue', marker='s', s=20, alpha=0.6)
    
    # Подписи и равный масштаб по всем осям (чтобы не искажало)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_box_aspect([1,1,1])  # равные пропорции осей
    plt.show()
    
A = (1, 1, 1)
B = (4, 1, 1)
C = (1, 3, 1)
D = (1, 1, 2)

voxels = voxelize_box(A, B, C, D, resolution=6)
visualize_voxels(voxels)