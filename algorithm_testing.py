def test_render_distance_cirle():
    size = 16
    render_distance = 3
    visualizer = [[[] for q in range(size)] for w in range(size)]

    middle_point = size//2
    val = 0
    for i in range(render_distance):
       up = i
       out = render_distance-i
       xpos = middle_point+i
       visualizer[xpos][middle_point] = [1]
       if i > 0:
        visualizer[middle_point-i][middle_point] = [6]
       for y in range(1, out):
            visualizer[xpos][middle_point+y] = [2]
            visualizer[xpos][middle_point-y] = [3]
            if i > 0:
                visualizer[middle_point-i][middle_point+y] = [4]
                visualizer[middle_point-i][middle_point-y] = [5]

       print(xpos, middle_point+y)
    #    for y in range(out):
    #        visualizer[middle_point+up][middle_point+y] = [1]
           
    #        #visualizer[middle_point-up][middle_point+y] = [2]
    #        #visualizer[middle_point+up][middle_point-y] = [3]
    #        visualizer[middle_point-up][middle_point-y] = [4]
    #        val += 4
    print(val)



    for v in visualizer:
        print(v)

def test_render_distance_squared_circle():
    size = 16
    render_distance = 3
    visualizer = [[[0] for q in range(size)] for w in range(size)]
    precomputed_distances = []
    middle_point = size//2
    r = render_distance
    r2 = r * r

    for dx in range(-r, r + 1):
        dz_max = int((r2 - dx*dx) ** 0.5)
        for dz in range(-dz_max, dz_max + 1):
            precomputed_distances.append([dx, dz])
    for v in visualizer:
        print(v)

    print(precomputed_distances)
    print(len(precomputed_distances))

test_render_distance_squared_circle()