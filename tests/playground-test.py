from readingTools import *
currDir = os.path.dirname(os.path.abspath(__file__))
feaPath = currDir + "/rules.fea"
feaDict = readFeaFile(feaPath)

# print(dict(enumerate(getFeaList(getFeaText(feaPath)))))
for n in feaDict:
	for m in feaDict[n]:
		print(m)
		print()
# for n in feaDict["blocks_0_deep"]:
# 	print("*******")
# 	print()
# 	print()
# 	print("*******")

# 	print(n["type"])
# 	if n["content"]:
# 		for m in n["content"]:
# 			print(m,">> ",n["content"][m])