import os
import tools
currDir = os.path.dirname(os.path.abspath(__file__))
feaPath = currDir + "/example.fea"

a = [1,2,3,4,5,6,7]
del a[2:4]
print(a)