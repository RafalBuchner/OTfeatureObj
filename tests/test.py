
#################
import random
import tools
# abc = "a b c d e f g h i j k l m n o p q r s t u v w x y z # & ^ * @ ( ) [ ] ~ 0 1 2 3 4 5 6 7 8 9".split(' ')
# abc = random.sample(abc,len(abc))
l = ["e1","feature","smcp","{","e2","lookup","mama","{","e3","e4","}","}","feature","liga","{","e7","lookup","fs","{","e8","e9","}","}","lookup","out","{","e10","e11","e12","}","lookup","out2","{","e13","e14","e15","}","feature","liga","{","e7","lookup","fs","{","e8","e9","}","}"]


openingEl = "{"
closingEl = "}"
def findNestedPairs(feaList,openingEl,closingEl):
	# returns dict, key:index in the fea list, value: (pairNumber, is opening element, nesting level)
	countOpening = -1
	countClosing = -1
	countPairs = -1
	pairDict = {} 

	ascendingList = []
	nestingList = []
	for i, el in enumerate(feaList):

		if el == openingEl:
			countOpening += 1
			countPairs += 1
			nestingLevel = countOpening

			pairDict[i] = (countPairs,True,nestingLevel)
			nestingList.append(nestingLevel)
			ascendingList.append(countPairs)
		if el == closingEl:
			nestingLevel = countOpening
			countOpening -= 1

			ascendingList.reverse()
			countClosing = ascendingList[0]
			del ascendingList[0]

			pairDict[i] = (countClosing,False,nestingLevel)
			nestingList.append(nestingLevel)


		if nestingList.count(0) == 2:
			nestingList = []
			ascendingList = []
	return pairDict

# parameters:
feaList = l
pairDict = findNestedPairs(l,"{","}")

# code:
feaList.append(None)
feaElements = [None for x in range(int(len(pairDict.keys())/2))]
feature = {}
lookup = {}
loadingFeatures = False
loadingLookup = False

for i, el in enumerate(feaList):
	if i in pairDict.keys():
		pairNum, isOpening, nestNum = pairDict[i]

		if feaList[i-2] == "feature" and isOpening:
			currentNest = nestNum
			feature = {}
			feature["data"] = {"type":feaList[i-2], "name":feaList[i-1], "nestNum":currentNest, "nestIndex":pairNum }
			loadingFeatures = True
			loadingLookup = False
			feature["elements"] = []

		if feaList[i-2] == "lookup" and isOpening:
			currentNest = nestNum
			lookup = {}
			lookup["data"] = {"type":feaList[i-2], "name":feaList[i-1], "nestNum":currentNest, "nestIndex":pairNum }
			loadingFeatures = False
			loadingLookup = True
			lookup["elements"] = []


		if loadingFeatures and not isOpening:
			feaElements[feature["data"]["nestIndex"]] = feature
			loadingFeatures = False
			feature = {}

		if loadingLookup and currentNest == nestNum and not isOpening:
			feaElements[lookup["data"]["nestIndex"]] = lookup
			loadingLookup = False
			if nestNum > 0:
				loadingFeatures = True
			elif nestNum == 0:
				print(lookup["elements"])
			lookup = {}

	if el != openingEl and el != closingEl:

		if loadingFeatures:
			feature["elements"].append(el)

		if loadingLookup:
			lookup["elements"].append(el)

	
# for el in feaElements:
# 	print(el)

# I'm assuming that there is not such a thing as nested features:
for i,el in enumerate(feaElements):
	if el["data"]["nestNum"] == 1:
		prev_el = feaElements[i-1]
		for i,sub_el in enumerate(prev_el["elements"]):
			if sub_el == el["data"]["type"]:
				prev_el[i] = el
		feaElements.remove(el)
print()
for i in feaElements:
	print(i)
