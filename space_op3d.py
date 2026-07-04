import numpy as np
import open3d as o3d

# 1. Параметры пространства и точек
space_bounds = np.array([[0.0, 0.0, 0.0], [1000.0, 500.0, 500.0]])
#print(space_bounds)
voxel_size = 30.0
start_pt = np.array([90.0, 316.77, 40.55])
finish_pt = np.array([830.0, 205.21, 390.0])

# 2. Препятствия (8 точек задет куб, всего 6 препяствий)
obstacles = [
    np.array([[174.89,136,38.71], [174.89,136,138.71], [274.89,136,138.71], [274.89,136,38.71], [174.89,236,38.71], [174.89,236,138.71], [274.89,236,138.71], [274.89,236,38.71]]),
    np.array([[174.89,61,288.71], [174.89,61,388.71], [274.89,61,388.71], [274.89,61,288.71], [174.89,161,288.71], [174.89,161,388.71], [274.89,161,388.71], [274.89,161,288.71]]),
    np.array([[460,227.99,173.28], [460,227.99,273.28], [560,227.99,273.28], [560,227.99,173.28], [460,327.99,173.28], [460,327.99,273.28], [560,327.99,273.28], [560,327.99,173.28]]),
    np.array([[460,183.99,398.28], [460,183.99,498.28], [560,183.99,498.28], [560,183.99,398.28], [460,283.99,398.28], [460,283.99,498.28], [560,283.99,498.28], [560,283.99,398.28]]),
    np.array([[674.89,61,288.71], [674.89,61,388.71], [774.89,61,388.71], [774.89,61,288.71], [674.89,161,288.71], [674.89,161,388.71], [774.89,161,388.71], [774.89,161,288.71]]),
    np.array([[865.98,275.15,60.24], [865.98,275.15,160.24], [965.98,275.15,160.24], [965.98,275.15,60.24], [865.98,375.15,60.24], [865.98,375.15,160.24], [965.98,375.15,160.24], [965.98,375.15,60.24]])
]

# 3. Создание пустой сетки. Получается 34х17х17 вокселей
dims = np.ceil((space_bounds[1] - space_bounds[0]) / voxel_size).astype(int)
grid = np.zeros(dims, dtype=int)

# 4. Заполнение препятствиями
for obs in obstacles:
    obs_min = np.floor((obs.min(axis=0) - space_bounds[0]) / voxel_size).astype(int) # округляем вниз | левый нижний воксель препятствия
    obs_max = np.ceil((obs.max(axis=0) - space_bounds[0]) / voxel_size).astype(int) # округляем вверх | правый верхний воксель препятствия
    
    # Защита от выхода за границы массива
    obs_min = np.clip(obs_min, 0, dims) # 
    obs_max = np.clip(obs_max, 0, dims) #
    
    print(obs_min, obs_max)
    
    grid[obs_min[0]:obs_max[0], obs_min[1]:obs_max[1], obs_min[2]:obs_max[2]] = 1 # заполянем сетку, 1 - препятсвие
    #print(grid[0])

# 5. Визуализация
obs_pts = space_bounds[0] + (np.argwhere(grid == 1) + 0.5) * voxel_size
pcd_obs = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(obs_pts))
pcd_obs.paint_uniform_color([0.8, 0.2, 0.2])

mesh_start = o3d.geometry.TriangleMesh.create_sphere(radius=15).translate(start_pt).paint_uniform_color([0, 1, 0])
mesh_finish = o3d.geometry.TriangleMesh.create_sphere(radius=15).translate(finish_pt).paint_uniform_color([0, 0, 1])
space_box = o3d.geometry.AxisAlignedBoundingBox(space_bounds[0], space_bounds[1])
space_box.color = [0, 0, 0]

o3d.visualization.draw_geometries([pcd_obs, space_box, mesh_start, mesh_finish], window_name="VoxelGrid")