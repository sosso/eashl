from pytesser import image_to_string
import PIL.Image as Image

def get_stats(path):
    image = Image.open(path)
    text = image_to_string(image)
    lines = text.split("\n")
    
    team1_vals = []
    team2_vals = []
    
    for line in lines:
        values = line.split(" ")
        val1 = values[0]
        val2 = values[len(values) - 1]
        team1_vals.append(val1)
        team2_vals.append(val2)
    return [team1_vals, team2_vals]
