from route import AstarSolver
from map import Map

# generate maze from image
map = Map("de_cache")
bit_map, dx, dy, point1 = map.bit_map, map.dx, map.dy, map.point1
# solve maze via solver
solver = AstarSolver(bitmap=bit_map)
solution = solver.solve_maze(start=((-1, -1),(47, 101)),end=((-1, -1),(41, 43)),radius=5,scale=1)
# visualize solution
solver.draw_routes(solution, bit_map, True)

print(solution)
