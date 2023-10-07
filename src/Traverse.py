def map_stack(skipw = width, skiph = height):
    for i in range(0, height, int(height / skiph)):
        for j in range(0, width, int(width / skipw)):
            hue = imghsv[i][j][0] # Take H value
            hues.append(hue)

def map_horizontal(skipw = width, skiph = height):
    for j in range(0, width, int(skipw % width)):
        for i in range(0, height, int(skiph % height)):
            hue = imghsv[i][j][0]
            hues.append(hue)

def map_vertical(skipw = width, skiph = height):
    for j in range(1, width, int(width / skipw)):
        for i in range(0, height, int(height /  skiph)):
            hue = imghsv[i][j][0]
            hues.append(hue)
