from route import AstarSolver,RRTSolver,BiRRTSolver
from map import Map

# generate maze from image
map = Map("de_dust2")

# solve maze via solver
#solver = AstarSolver(map_=map)
#solution = solver.solve_maze(start=(178,57),end=(31, 159),radius=80,scale=1)
# solver = RRTSolver(map_=map)
# solution = solver.solve_maze(start=(178,57),end=(31, 159),radius=3,iter=2000,step_num=5,step_len=2)
solver = BiRRTSolver(map_=map)
solution = solver.solve_maze(start=(178,57),end=(31, 159),radius=2,iter=5000,step_num=2,step_len=1,prob=0.9,draw=1)



# visualize solution
solver.draw_routes(solution, map.bit_map, True)

print(solution)
