from sage.all import matrix, vector, RR, QQ, show, InteractiveLPProblem, MixedIntegerLinearProgram
import sys
import bisect

N = 6 # NxN grid
corners = []
sides = []
middles = []

# pokazuje intuicyjną reprezentację danego kafelka; wymaga listy stringów z co najmniej 3 elementami
def showTile(lines, tile):
    lines[-3] += "⌜"+str(tile[0])+"⌝"
    lines[-2] += str(tile[3])+" "+str(tile[1])
    lines[-1] += "⌞"+str(tile[2])+"⌟"

# organizuje wejście
def getInput(tiles):

    N = int(input())
    for i in range(N*N):
         tiles.append(input().split(" "))
         for j in range(len(tiles[-1])): tiles[-1][j] = int(tiles[-1][j])

# obraca kafelek r-razy o 90 stopni, zgodnie ze wskazówkami zegara
def rotateTile(t, r):
    return [t[-r], t[1-r], t[2-r], t[3-r]]

# klasyfikowanie i organizacja kafelków
def classifyTiles(tiles):
    for t in tiles:
        temp = sum((t[i] == 0) for i in range(4))
        if   temp == 2: # obracanie w taki sposób, żeby wartości 0 znajdowały się przy prawych górnym rogu
            if   t[2] != 0 and t[3] == 0: corners.append(rotateTile(t, 0))
            elif t[3] != 0 and t[0] == 0: corners.append(rotateTile(t, 3))
            elif t[0] != 0 and t[1] == 0: corners.append(rotateTile(t, 2))
            else                        : corners.append(rotateTile(t, 1))
        elif temp == 1: # obracanie w taki sposób, żeby wartości 0 znajdowały się przy górnej krawędzi
            if   t[0] == 0: sides.append(rotateTile(t, 0))
            elif t[1] == 0: sides.append(rotateTile(t, 3))
            elif t[2] == 0: sides.append(rotateTile(t, 2))
            else          : sides.append(rotateTile(t, 1))
        elif temp == 0: middles.append(t)
        else: print("!BŁĄD! Kafelek z błędną liczbą krawędzi bocznych")

# tworzy wszystkie możliwe obroty kafelków
def getRotations(ogMiddles):
    middles = []
    for t in ogMiddles:
        for r in range(4):
            middles.append(rotateTile(t, r))
    return middles

# zwraca sumę zmiennej obecności wszystkich kafelków na danych koordynatach
def getBoolAtCoords(grid, x, y):
    if   (x == 0 or x == N-1) and (y == 0 or y == N-1): # Rogi
        return sum(grid[x, y, n] for n in range(len(corners)))
    elif (x == 0 or x == N-1) or  (y == 0 or y == N-1): # Brzegi
        return sum(grid[x, y, n] for n in range(len(sides)))
    else:
        return sum(grid[x, y, n] for n in range(len(middles)))

# zwraca sumę krawędzi wszystkich kafelków na danych koordynatach i na danej stronie
def getValueAtCoords(grid, x, y, s):
    if   (x == 0 or x == N-1) and (y == 0 or y == N-1): # Rogi
        if   x == N-1 and y == 0  : s -= 1
        elif x == N-1 and y == N-1: s -= 2
        elif x == 0   and y == N-1: s -= 3
        s = s % 4
        return sum(grid[x, y, n] * corners[n][s] for n in range(len(corners)))
    elif (x == 0 or x == N-1) or  (y == 0 or y == N-1): # Brzegi
        if x == N-1: s -= 1
        if y == N-1: s -= 2
        if x == 0  : s -= 3
        s = s % 4
        return sum(grid[x, y, n] * sides[n][s] for n in range(len(sides)))
    else:
        return sum(grid[x, y, n] * middles[n][s] for n in range(len(middles)))

# kluczowa funkcja, rozwiązuje problem optymalizacją liniową
def solve():
    lp = MixedIntegerLinearProgram(maximization=True)
    grid = lp.new_variable(binary=True)
    lp.set_objective(1)

    # warunek jednokrotnego wykorzystania kafelka
    for x in range(N):
        for y in range(N):
            lp.add_constraint(getBoolAtCoords(grid, x, y) == 1)

    # warunek jednokrotnego wykorzystania obrotu kafelka środkowego
    for n in range(0, len(middles), 4):
        lp.add_constraint(sum(sum(sum(grid[x, y, n+i] for i in range(4))
                                  for x in range(1, N-1))
                              for y in range(1, N-1)) == 1)

    # warunek krawędzi z wartością 0 na zewnątrz
    # górny brzeg
    for x in range(N):
        lp.add_constraint(getValueAtCoords(grid, x  , 0  , 0) == 0)
    # prawy brzeg
    for y in range(N):
        lp.add_constraint(getValueAtCoords(grid, N-1, y  , 1) == 0)
    # dolny brzeg
    for y in range(N):
        lp.add_constraint(getValueAtCoords(grid, x  , N-1, 2) == 0)
    # prawy brzeg
    for y in range(N):
        lp.add_constraint(getValueAtCoords(grid, 0  , y  , 3) == 0)

    # kluczowy warunek: wszystkie krawędzie muszą mieć takie same wartości na obu kafelkach
    for x in range(N):
        for y in range(N):
            if x < N-1: lp.add_constraint(getValueAtCoords(grid, x  , y  , 1) ==
                                          getValueAtCoords(grid, x+1, y  , 3))
            if y < N-1: lp.add_constraint(getValueAtCoords(grid, x  , y  , 2) ==
                                          getValueAtCoords(grid, x  , y+1, 0))
    
    lp.solve()
    dict = lp.get_values(grid)
    result = [[-1 for x in range(N)] for y in range(N)]
    
    for a in dict:
        if dict[a] == 1: result[a[1]][a[0]] = a[2]

    return result






ogTiles = []

getInput(ogTiles)
classifyTiles(ogTiles)
middles = getRotations(middles)
         
result = solve()

representation = []
for x in range(len(result)):
    for i in range(3): representation.append("")
    for y in range(len(result[x])):
        s = 0
        if   (x == 0 or x == N-1) and (y == 0 or y == N-1):            
            if   x == N-1 and y == 0  : s = 3
            elif x == N-1 and y == N-1: s = 2
            elif x == 0   and y == N-1: s = 1
            showTile(representation, rotateTile(corners[result[x][y]], s))
        elif (x == 0 or x == N-1) or  (y == 0 or y == N-1): # Brzegi
            if   y == N-1: s = 1
            elif x == N-1: s = 2
            elif y == 0  : s = 3
            showTile(representation, rotateTile(sides  [result[x][y]], s))
        else: showTile(representation, middles[result[x][y]])

for r in representation:
    print(r)
