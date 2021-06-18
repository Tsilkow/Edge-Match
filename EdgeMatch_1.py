from sage.all import matrix, vector, RR, QQ, show, InteractiveLPProblem, MixedIntegerLinearProgram
import sys
import bisect

def showTile(lines, tile):
    lines[-3] += "⌜"+str(tile[0])+"⌝"
    lines[-2] += str(tile[3])+" "+str(tile[1])
    lines[-1] += "⌞"+str(tile[2])+"⌟"

N = 4 # NxN grid

#           [N, E, S, W]
oldTiles = [[1, 2, 3, 4], # 1
            [1, 2, 3, 4], # 2
            [1, 2, 3, 4], # 3
            [1, 2, 3, 4], # 4
            [1, 2, 3, 4], # 5
            [1, 2, 3, 4], # 6
            [1, 2, 3, 4], # 7
            [1, 2, 3, 4], # 8
            [1, 2, 3, 4], # 9
            [1, 2, 3, 4], # 10
            [1, 2, 3, 4], # 11
            [1, 2, 3, 4], # 12
            [1, 2, 3, 4], # 13
            [1, 2, 3, 4], # 14
            [1, 2, 3, 4], # 15
            [1, 2, 3, 4]] # 16

#           [N, E, S, W]
oldTiles = [[1, 2, 3, 5], # 1
            [5, 4, 6, 2], # 2
            [1, 5, 3, 4], # 3
            [2, 1, 6, 5], # 4
            [6, 2, 3, 4], # 5
            [3, 4, 2, 5], # 6
            [6, 5, 4, 1], # 7
            [3, 1, 6, 2], # 8
            [6, 3, 4, 5], # 9
            [4, 1, 2, 3], # 10
            [2, 5, 4, 1], # 11
            [3, 1, 6, 5], # 12
            [4, 6, 1, 2], # 13
            [2, 3, 5, 6], # 14
            [4, 1, 6, 3], # 15
            [6, 3, 2, 1]] # 16

#oldTiles = [[1, 2, 3, 4],
#            [5, 6, 7, 2],
#            [3, 8, 9, 10],
#            [7, 11, 12, 8]]
         

lp = MixedIntegerLinearProgram(maximization=True)

grid = lp.new_variable(binary=True)
#rotations = lp.new_variable(binary=True)

lp.set_objective(1)

tiles = []
for t in oldTiles:
    tiles.append(t)
    tiles.append([t[3], t[0], t[1], t[2]])
    tiles.append([t[2], t[3], t[0], t[1]])
    tiles.append([t[1], t[2], t[3], t[0]])

#for n in range(len(tiles)):
#    lp.add_constraint(sum(rotations[n, s] for s in range(4)) == 1)

# ograniczenia na przypisanie jednego i tylko jednego kafelka do danej kratki
for x in range(N):
    for y in range(N):
        lp.add_constraint(sum(grid[x, y, n] for n in range(len(tiles))) == 1)

for n in range(0, len(tiles), 4):
    lp.add_constraint(sum(sum(sum(grid[x, y, n+i] for i in range(4)) for x in range(N)) for y in range(N)) == 1)

# ograniczeni
for x in range(N):
    for y in range(N):
        #if x > 0: lp.add_constraint(sum( grid[x  ][y][n] * tiles[n][(3 + rotations[n]) % 4]
        #                                -grid[x-1][y][n] * tiles[n][(1 + rotations[n]) % 4]
        #                                 for n in range(len(tiles))) == 0)
        # 
        #if y > 0: lp.add_constraint(sum( grid[x][y  ][n] * tiles[n][(0 + rotations[n]) % 4]
        #                                -grid[x][y-1][n] * tiles[n][(2 + rotations[n]) % 4]
        #                                 for n in range(len(tiles))) == 0)
        #
        if x < N-1: lp.add_constraint(sum(grid[x  , y, n] * tiles[n][1] - grid[x+1, y, n] * tiles[n][3]
                                          for n in range(len(tiles))) == 0)
    
        if y < N-1: lp.add_constraint(sum(grid[x, y  , n] * tiles[n][2] - grid[x, y+1, n] * tiles[n][0]
                                          for n in range(len(tiles))) == 0)
    
lp.show()
lp.solve()
print(lp.get_values(grid))

dict = lp.get_values(grid)
result = [[[-1, 0] for x in range(N)] for y in range(N)]

for a in dict:
    if dict[a] == 1: result[a[1]][a[0]] = [a[2]//4, a[2] - a[2]//4*4]

for r in result:
    print(r)

representation = ["", "", ""]
    
for r in result:
    for c in r:
        showTile(representation, tiles[c[0]*4 + c[1]])
    for i in range(3): representation.append("")

for r in representation:
    print(r)
    
