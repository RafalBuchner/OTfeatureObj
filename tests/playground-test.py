from toolsTemp import *
currDir = os.path.dirname(os.path.abspath(__file__))
feaPath = currDir + "/supersimple.fea"
feaDict = readFeaFile(feaPath)


for n in feaDict["blocks_0_deep"]:
	print("*******")
	print()
	print()
	print("*******")

	print(n["type"])
	if n["content"]:
		for m in n["content"]:
			print(m,">> ",n["content"][m])