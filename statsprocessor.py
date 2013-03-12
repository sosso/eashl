from pytesser import image_to_string
import PIL.Image as Image
import os
import urllib2 as urllib
import cStringIO

def get_stats(url):
    file = cStringIO.StringIO(urllib.urlopen(url).read())
    image = Image.open(file)
    text2 = image_to_string(image)
    lines2 = text2.split("\n")
    team1_vals = []
    team2_vals = []
    
    for line in lines2:
        values = line.split(" ")
        val1 = values[0]
        val2 = values[len(values)-1]
        team1_vals.append(val1)
        team2_vals.append(val2)
    return [team1_vals, team2_vals]