import os
import tools

feaList = ["e1","feature",
"smcp","{","e2",
"lookup","mama","{","e3","e4","}",
"}",
"feature","liga","{","e7","lookup","fs","{","e8","e9","}","}","lookup","out","{","e10","e11","e12","}","lookup","out2","{","e13","e14","e15","}","feature","liga","{","e7","lookup","fs","{","e8","e9","}","}"]
f = [1,2,3]
f.pop(1)
print(f)

#######
# currDir = os.path.dirname(os.path.abspath(__file__))
# feaPath = currDir + "/supersimple.fea"
# feaList = tools.stripFea(feaPath)

# openingEl = "{"
# # closingEl = "}"
# feaElements = tools.getFeaturesAndLookups(feaList)
# for i in feaElements:
# 	# print(i)
# 	print(i)
# 	for j in i["elements"]:
# 		print(">>>> ",j)

