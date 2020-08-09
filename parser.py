import os,re

with open("fruits.txt","r") as f:
    lines = f.readlines()
    matches = re.findall("[0-9]+\.[a-z]+", lines[0])
    print("\n".join([m.split(".")[1] for m in matches]))