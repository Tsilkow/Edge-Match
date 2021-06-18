from sage.all import matrix, vector, RR, QQ, show, InteractiveLPProblem, MixedIntegerLinearProgram
import sys
import bisect

# pokazuje intuicyjną reprezentację danego kafelka; wymaga listy stringów z co najmniej 3 elementami
def showTile(lines, tile):
    lines[-3] += "⌜"+str(tile[0])+"⌝"
    lines[-2] += str(tile[3])+" "+str(tile[1])
    lines[-1] += "⌞"+str(tile[2])+"⌟"

# organizuje wejście
def getInput(N, tiles):

    N = int(input())
    for i in range(N*N):
         tiles.append(input().split(" "))

# tworzy wszystkie możliwe obroty kafelków
def getRotations(ogTiles):
    tiles = []
    for t in ogTiles:
        tiles.append(t)
        tiles.append([t[3], t[0], t[1], t[2]])
        tiles.append([t[2], t[3], t[0], t[1]])
        tiles.append([t[1], t[2], t[3], t[0]])
    return tiles

# kluczowa funkcja, rozwiązuje problem optymalizacją liniową
def solve(N, tiles):
    lp = MixedIntegerLinearProgram(maximization=True)
    grid = lp.new_variable(binary=True)
    lp.set_objective(1)
    
    # ograniczenia na przypisanie jednego i tylko jednego kafelka do danej kratki
    for x in range(N):
        for y in range(N):
            lp.add_constraint(sum(grid[x, y, n] for n in range(len(tiles))) == 1)

    # ograniczenia na przypisanie jednego i tylko jednego obrotu kafelka do jakiejkolwiek kratki
    for n in range(0, len(tiles), 4):
        lp.add_constraint(sum(sum(sum(grid[x, y, n+i] for i in range(4)) for x in range(N)) for y in range(N)) == 1)

    # kluczowy warunek na krawędzie: kafelki po obu stronach musza mieć tę samą wartość na odpowiadających bokach
    for x in range(N):
        for y in range(N):
            if x < N-1: lp.add_constraint(sum(grid[x  , y, n] * tiles[n][1] - grid[x+1, y, n] * tiles[n][3]
                                              for n in range(len(tiles))) == 0)
            
            if y < N-1: lp.add_constraint(sum(grid[x, y  , n] * tiles[n][2] - grid[x, y+1, n] * tiles[n][0]
                                              for n in range(len(tiles))) == 0)

    lp.solve()
    dict = lp.get_values(grid)
    result = [[[-1, 0] for x in range(N)] for y in range(N)] # pairs of [n, s], where n is index of tile and s is rotation
    
    for a in dict:
        if dict[a] == 1: result[a[1]][a[0]] = [a[2]//4, a[2] - a[2]//4*4]

    return result





N = 4 # NxN grid
ogTiles = []

getInput(N, ogTiles)
tiles = getRotations(ogTiles)
         
result = solve(N, tiles)

representation = []
for r in result:
    for i in range(3): representation.append("")
    for c in r:
        showTile(representation, tiles[c[0]*4 + c[1]])

for r in representation:
    print(r)
