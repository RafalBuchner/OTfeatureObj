import os
import re

special_Characters = ("[", "]", "{", "}", ";", "#")
special_Expressions = ("languagesystem", "feature",
                       "lookup", "pos", "sub", "by")


def replaceAtIndex(l1, l2, i):
    l2.reverse()
    del l1[i]
    for x in l2:
        l1.insert(i, x)
    return l1


def separate_txt_by(txt, sep):
    import re
    return [x for x in re.split(f"({sep})", txt) if x != '']


def getItemsBetweenElemnts(array, openingEl, closingEl):
    openAdding = False
    list_of_values = {}

    for i, x in enumerate(array):
        if x == openingEl:

            openAdding = True
        elif x == closingEl and openAdding == True:
            list_of_values[value[0]] = value[1]
            openAdding = False
        else:
            if openAdding:
                value = (i, x)

    return list_of_values


def stripFea(path):

    assert path.split(
        '/')[-1].split('.')[-1] == "fea", "passed file is not a OT-feature file"
    file = open(path, "r")
    fea_text = file.read()
    fea_text_list_temp = []
    for element in fea_text.split(' '):
        if len(element) > 0:
            for sub_element in separate_txt_by(element, '\n'):

                fea_text_list_temp.append(sub_element)

    for i, element in enumerate(fea_text_list_temp):
        if "\t" in element:
            fea_text_list_temp[i] = element.replace("\t", "")

    fea_text_list = []
    for element in fea_text_list_temp:
        skip = False  # flow control
        temp = []
        for char in special_Characters:
            if char in element:
                position = element.find(char)
                new_element = element.replace(char, "")
                more_special_chars = False

                for char_b in special_Characters:
                    if char_b in new_element:
                        more_special_chars = True

                if more_special_chars:
                    temp.append(char)
                    continue

                if position == 0 and new_element != "":
                    fea_text_list.append(char)
                    fea_text_list.append(new_element)
                    skip = True

                elif element[position] == element[-1] and new_element != "":
                    fea_text_list.append(new_element)
                    fea_text_list.append(char)

                    skip = True
        if skip:
            skip = False
            continue

        if element != "":
            for char in special_Characters:
                if char in element and len(element) > 1:
                    element = element.replace(char, "")

            fea_text_list.append(element)

            if len(temp) > 0:
                for char in temp:
                    fea_text_list.append(char)

    for x in range(3):  # getting rid of unnescessary line breaks
        for i, element in enumerate(fea_text_list):
            if i + 1 < len(fea_text_list):
                if element == "\n" and fea_text_list[i + 1] == element:
                    del fea_text_list[i + 1]

    return fea_text_list


def findNestedPairs(feaList, openingEl, closingEl):
    # returns dict, key:index in the fea list, value: (pairNumber, is opening
    # element, nesting level)
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

            pairDict[i] = (countPairs, True, nestingLevel)
            nestingList.append(nestingLevel)
            ascendingList.append(countPairs)
        if el == closingEl:
            nestingLevel = countOpening
            countOpening -= 1

            ascendingList.reverse()
            countClosing = ascendingList[0]
            del ascendingList[0]

            pairDict[i] = (countClosing, False, nestingLevel)
            nestingList.append(nestingLevel)

        if nestingList.count(0) == 2:
            nestingList = []
            ascendingList = []
    return pairDict


def getFeaturesAndLookups(feaList):
    """
            TODO:
            elements zastąb następującymi kategoriami:
            rules, lookup declarations, lookup calls
    """
    openingEl, closingEl = ("{", "}")
    pairDict = findNestedPairs(feaList, openingEl, closingEl)

    feaElements = [None for x in range(int(len(pairDict.keys()) / 2))]
    feature = {}
    lookup = {}
    loadingFeatures = False
    loadingLookup = False

    # próbjuję się pozbyć powtórek w "elements"
    for i in getItemsBetweenElemnts(feaList, "}", ";"):
    	feaList[i] = None

    for i, el in enumerate(feaList):
        if i in pairDict.keys():
            pairNum, isOpening, nestNum = pairDict[i]

            if feaList[i - 2] == "feature" and isOpening:
                currentNest = nestNum
                feature = {}
                feature["data"] = {"type": feaList[
                    i - 2], "name": feaList[i - 1], "nestNum": currentNest, "nestIndex": pairNum}

                feaList[i - 1] = None

                loadingFeatures = True
                loadingLookup = False
                feature["elements"] = []

            if feaList[i - 2] == "lookup" and isOpening:
                currentNest = nestNum
                lookup = {}
                lookup["data"] = {"type": feaList[
                    i - 2], "name": feaList[i - 1], "nestNum": currentNest, "nestIndex": pairNum}

                feaList[i - 1] = None

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

                lookup = {}
        if el:
	        if el != openingEl and el != closingEl:

	            if loadingFeatures:
            		feature["elements"].append(el)

	            if loadingLookup:
                	lookup["elements"].append(el)

    # # I'm assuming that there is not such a thing as nested features:
    for i, el in enumerate(feaElements):
        if el["data"]["nestNum"] == 1:
            prev_el = feaElements[i - 1]
            for i, sub_el in enumerate(prev_el["elements"]):
                if sub_el == el["data"]["type"]:
                    prev_el["elements"][i] = el
            feaElements.remove(el)

    for el in feaElements:
    	els = el['elements']
    	for i,subEl in enumerate(els):
    		if type(subEl) == dict:
    			if els[i+1] == subEl['data']['name'] and els[i+2] == ";":
    				els[i+1] = None
    				els[i+2] = None
    	# for i,subEl in enumerate(els):
    	# 	if not subEl:
    	# 		del subEl
    			

    return feaElements

currDir = os.path.dirname(os.path.abspath(__file__))
feaPath = currDir + "/supersimple.fea"
feaList = stripFea(feaPath)

openingEl = "{"
# closingEl = "}"
feaElements = getFeaturesAndLookups(feaList)
for i in feaElements:
	# print(i)
	print(i)
	print()
	# for j in i["elements"]:
	# 	print(">>>> ",j)
