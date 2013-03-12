from pytesser import image_to_string
import PIL.Image as Image
import os

def get_stats(url, image_data):
    path = url.split("/")[-1]
    f = open(path, 'wb')
    f.write(image_data)
    f.close()
    image = Image.open(path)
    text2 = image_to_string(image)
    lines2 = text2.split("\n")
    os.remove(path)
    
    team1_vals = []
    team2_vals = []
    
    for line in lines2:
        values = line.split(" ")
        val1 = values[0]
        val2 = values[len(values)-1]
        team1_vals.append(val1)
        team2_vals.append(val2)
    return [team1_vals, team2_vals]