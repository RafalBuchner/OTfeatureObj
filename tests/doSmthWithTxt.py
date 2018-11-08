import os

currDir = os.path.dirname(os.path.abspath(__file__))
path = currDir + './00_punctuation.txt'
f = open(path,'r')
print(f.readlines())
