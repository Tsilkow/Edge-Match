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

def classifyTiles(tiles, corners, sides, middles):
    corners = []
    sides = []
    middles = []
    for t in tiles:
        temp = sum(tiles[i] == 0 for i in range(4))
        if   temp == 2: corners.append(t)
        elif temp == 1: sides.append(t)
        elif temp == 0: middles.append(t)
        else: print("!BŁĄD! Kafelek z błędną liczbą krawędzi bocznych")

# tworzy wszystkie możliwe obroty kafelków
def getRotations(ogMiddles):
    middles = []
    for t in ogMiddles:
        middles.append(t)
        middles.append([t[3], t[0], t[1], t[2]])
        middles.append([t[2], t[3], t[0], t[1]])
        middles.append([t[1], t[2], t[3], t[0]])
    return middles

# kluczowa funkcja, rozwiązuje problem optymalizacją liniową
def solve(N, tiles):
    lp = MixedIntegerLinearProgram(maximization=True)
    grid = lp.new_variable(binary=True)
    lp.set_objective(1)

    # warunki na rogi
    lp.add_constraint(sum(grid[0  , 0  , n] for n in range(len(corners))) == 1)
    lp.add_constraint(sum(grid[N-1, 0  , n] for n in range(len(corners))) == 1)
    lp.add_constraint(sum(grid[N-1, N-1, n] for n in range(len(corners))) == 1)
    lp.add_constraint(sum(grid[0  , N-1, n] for n in range(len(corners))) == 1)

    # warunki na brzegi
    # górny brzeg
    for x in range(1, N-2): lp.add_constraint(sum(grid[x  , 0  , n] for n in range(len(sides))) == 1)
    # prawy brzeg
    for y in range(1, N-2): lp.add_constraint(sum(grid[N-1, y  , n] for n in range(len(sides))) == 1)
    # dolny brzeg
    for x in range(1, N-2): lp.add_constraint(sum(grid[x  , N-1, n] for n in range(len(sides))) == 1)
    # lewy brzeg
    for y in range(1, N-2): lp.add_constraint(sum(grid[0  , y  , n] for n in range(len(sides))) == 1)

    # warunki na środki
    # ograniczenia na przypisanie jednego i tylko jednego środka do danej kratki
    for x in range(1, N-1):
        for y in range(1, N-1):
            lp.add_constraint(sum(grid[x, y, n] for n in range(len(middles))) == 1)

    # ograniczenia na przypisanie jednego i tylko jednego obrotu środka do jakiejkolwiek kratki
    for n in range(0, len(middles), 4):
        lp.add_constraint(sum(sum(sum(grid[x, y, n+i] for i in range(4))
                                  for x in range(1, N-1))
                              for y in range(1, N-1)) == 1)

    # krańce planszy
    # górna ściana
    lp.add_constraint(sum(grid[0, 0, n] * corners[n][0] for n in range(len(corners))) == 0)
    for x in range(1, N-1):
        lp.add_constraint(sum(grid[N-1, 0, n] * sides[n][0] for n in range(len(sides))) == 0)
    

    # połączenia róg - brzeg
    # róg 0, 0
    lp.add_constraint(sum(grid[0, 0, n] * corners[n][1] for n in range(len(corners))) ==
                      sum(grid[1, 0, n] * sides  [n][3] for n in range(len(sides  ))))    
    lp.add_constraint(sum(grid[0, 0, n] * corners[n][2] for n in range(len(corners))) ==
                      sum(grid[0, 1, n] * sides  [n][0] for n in range(len(sides  ))))
    # róg N-1, 0
    lp.add_constraint(sum(grid[N-1, 0, n] * corners[n][3] for n in range(len(corners))) ==
                      sum(grid[N-2, 0, n] * sides  [n][1] for n in range(len(sides  ))))    
    lp.add_constraint(sum(grid[N-1, 0, n] * corners[n][2] for n in range(len(corners))) ==
                      sum(grid[N-1, 1, n] * sides  [n][0] for n in range(len(sides  ))))
    # róg N-1, N-1
    lp.add_constraint(sum(grid[N-1, N-1, n] * corners[n][3] for n in range(len(corners))) ==
                      sum(grid[N-2, N-1, n] * sides  [n][1] for n in range(len(sides  ))))    
    lp.add_constraint(sum(grid[N-1, N-1, n] * corners[n][0] for n in range(len(corners))) ==
                      sum(grid[N-1, N-2, n] * sides  [n][2] for n in range(len(sides  ))))
    # róg 0, N-1
    lp.add_constraint(sum(grid[0, N-1, n] * corners[n][1] for n in range(len(corners))) ==
                      sum(grid[1, N-1, n] * sides  [n][3] for n in range(len(sides  ))))    
    lp.add_constraint(sum(grid[0, N-1, n] * corners[n][0] for n in range(len(corners))) ==
                      sum(grid[0, N-2, n] * sides  [n][2] for n in range(len(sides  ))))

    # połączenia brzeg-brzeg
    # górna ściana
    for x in range(1, N-2): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[x, 0, n] * sides[n][1] - grid[x+1, 0, n] * sides[n][3]
                              for n in range(len(sides))) == 0)
    # prawa ściana
    for y in range(1, N-2): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[N-1, y, n] * sides[n][2] - grid[N-1, y+1, n] * sides[n][3]
                              for n in range(len(sides))) == 0)
    # dolna ściana
    for x in range(1, N-2): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[x, N-1, n] * sides[n][1] - grid[x+1, N-1, n] * sides[n][3]
                              for n in range(len(sides))) == 0)
    # lewa ściana
    for y in range(1, N-2): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[0, y, n] * sides[n][2] - grid[0, y+1, n] * sides[n][3]
                              for n in range(len(sides))) == 0)

    # połączenia brzeg-środek
    # górna ściana
    for x in range(1, N-1): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[x, 0, n] * sides  [n][2] for n in range(len(sides  ))) ==
                          sum(grid[x, 0, n] * middles[n][0] for n in range(len(middles))))
    # prawa ściana
    for y in range(1, N-1): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[N-1, y, n] * sides  [n][3] for n in range(len(sides  ))) ==
                          sum(grid[N-2, y, n] * middles[n][1] for n in range(len(middles))))
    # dolna ściana
    for x in range(1, N-1): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[x, N-1, n] * sides  [n][0] for n in range(len(sides  ))) ==
                          sum(grid[x, N-1, n] * middles[n][2] for n in range(len(middles))))
    # lewa ściana
    for y in range(1, N-1): # bez rogów i ostatniego na ściance (bo ten łączy się z rogiem)
        lp.add_constraint(sum(grid[0, y, n] * sides  [n][1] for n in range(len(sides  ))) ==
                          sum(grid[1, y, n] * middles[n][3] for n in range(len(middles))))

    # połączenia środek-środek


    # kluczowy warunek na krawędzie: kafelki po obu stronach musza mieć tę samą wartość na odpowiadających bokach
    for x in range(1, N-1):
        for y in range(1, N-1):
            if x < N-2: lp.add_constraint(sum(grid[x  , y, n] * middles[n][1] - grid[x+1, y, n] * middles[n][3]
                                              for n in range(len(middles))) == 0)
            
            if y < N-2: lp.add_constraint(sum(grid[x, y  , n] * middles[n][2] - grid[x, y+1, n] * middles[n][0]
                                              for n in range(len(middles))) == 0)

    lp.solve()
    dict = lp.get_values(grid)
    result = [[-1 for x in range(N)] for y in range(N)] # pairs of [n, s], where n is index of tile and s is rotation
    
    for a in dict:
        if dict[a] == 1: result[a[1]][a[0]] = a[2]

    return result





N = 4 # NxN grid
ogTiles = []

getInput(N, ogTiles)
corners = []
sides = []
middles = []
classifyTiles(ogTiles, corners, sides, middles)
middles = getRotations(middles)
         
result = solve(N, corners, sides, middles)

representation = []
for r in range(len(result)):
    for i in range(3): representation.append("")
    for c in range(len(result[r])):
        if   r == c and c == 0: showTile(representation, corners[result[r][c]])
        elif r == 0 or  c == 0: showTile(representation, sides  [result[r][c]])
        else                  : showTile(representation, middles[result[r][c]])

for r in representation:
    print(r)
