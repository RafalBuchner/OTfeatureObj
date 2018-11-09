import os
import re
import copy

special_Characters = ("[", "]", "{", "}", "<", ">", ";", "#", "||||||||||||")
special_Expressions = ("languagesystem", "feature",
                       "lookup", "pos", "sub", "by",)
strdigits = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0",)


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
    list_of_values = []
    value = []
    for x in array:
        if x == openingEl:
            value = []
            openAdding = True
        elif x == closingEl and openAdding == True:
            list_of_values.append(value)
            openAdding = False
        else:
            if openAdding:
                value.append(x)

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

# delete whole function?:


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
    countDeletingUnnecessaryLookupNames = 0  # WIP
    lastLookupName = ""  # WIP
    ###
    for i, el in enumerate(feaList):
        if i in pairDict.keys():
            pairNum, isOpening, nestNum = pairDict[i]

            if feaList[i - 2] == "feature" and isOpening:
                currentNest = nestNum
                feature = {}
                feature["data"] = {"type": feaList[
                    i - 2], "name": feaList[i - 1], "nestNum": currentNest, "nestIndex": pairNum}
                loadingFeatures = True
                loadingLookup = False
                feature["elements"] = []

            if feaList[i - 2] == "lookup" and isOpening:
                currentNest = nestNum
                lookup = {}
                lookup["data"] = {"type": feaList[
                    i - 2], "name": feaList[i - 1], "nestNum": currentNest, "nestIndex": pairNum}
                loadingFeatures = False
                loadingLookup = True
                lookup["elements"] = []
                lastLookupName = ""  # WIP

            if loadingFeatures and not isOpening:
                feaElements[feature["data"]["nestIndex"]] = feature
                loadingFeatures = False
                feature = {}

            if loadingLookup and currentNest == nestNum and not isOpening:
                feaElements[lookup["data"]["nestIndex"]] = lookup
                loadingLookup = False
                if nestNum > 0:
                    loadingFeatures = True

                lastLookupName = lookup["data"]["name"]  # WIP
                lookup = {}

        if el != openingEl and el != closingEl:

            if el == lastLookupName:  # WIP
                countDeletingUnnecessaryLookupNames += 1  # WIP
            print(countDeletingUnnecessaryLookupNames)  # WIP
            print(lastLookupName)  # WIP
            if loadingFeatures:
                feature["elements"].append(el)

            if loadingLookup:
                lookup["elements"].append(el)

    # # I'm assuming that there is not such a thing as nested features:
    for i, el in enumerate(feaElements):
        if el["data"]["nestNum"] == 1:
            print(type(feaElements[i - 1]))
            prev_el = feaElements[i - 1]
            for i, sub_el in enumerate(prev_el["elements"]):
                if sub_el == el["data"]["type"]:
                    prev_el["elements"][i] = el
            feaElements.remove(el)
    return feaElements


def getBlocks(feaList):
    """
        returns set of dicts
    """
    def _getCorrespondingBraceIndex(indexOfBrace, braceDict):
        closing_index = None
        search_pairIndex, search_isOpening, search_deepLeve = (
            None, None, None)
        for index in braceDict:
            pairIndex, isOpening, deepLevel = braceDict[index]
            if index == indexOfBrace:
                search_pairIndex, search_isOpening, search_deepLevel = braceDict[
                    index]
            if pairIndex == search_pairIndex and isOpening != search_isOpening and deepLevel == search_deepLevel:
                closing_index = index
        return closing_index
    ##########
    # BLOCKS #
    ##########
    # creating the dictionary of feaList items, with indexes as a key.
    # It will be useful in deleting by orginal index
    indexed_feaDict = {}
    for i, x in enumerate(feaList):
        indexed_feaDict[i] = x

    openingEl, closingEl = ("{", "}")
    nestedPairs = findNestedPairs(feaList, openingEl, closingEl)

    blocks = []

    block_index = 0
    for i in indexed_feaDict:
        element = indexed_feaDict[i]

        if element == openingEl:
            block_descrpition = {}
            opening_Index = i
            closing_index = _getCorrespondingBraceIndex(i, nestedPairs)
            block_descrpition["type"] = f"{feaList[i - 2]}-block"
            block_descrpition["name"] = feaList[i - 1]
            block_descrpition["deepLevel"] = nestedPairs[i][2]
            block_descrpition["index"] = block_index
            block_descrpition["feaList_index_range"] = (
                opening_Index - 2, closing_index + 3)  # range of global indexes
            block_descrpition["content"] = feaList[
                opening_Index + 1:closing_index]
            blocks.append(block_descrpition)

    # deleting the blocks from indexed_feaDict
    indexed_feaDict_wthout_blocks = copy.deepcopy(indexed_feaDict)
    blocks_0_deep = []
    index_0_deep = 0

    for block in blocks:
        start_Index, end_index = block["feaList_index_range"]
        indexes_to_remove = []
        for i in indexed_feaDict_wthout_blocks:

            if i >= start_Index and i <= end_index:
                indexes_to_remove.append(i)
        for i in indexes_to_remove:
            indexed_feaDict_wthout_blocks.pop(i)

        # getting read of deeper levels
        # deeper levels are still stored in blocks list
        # Later if I would like to check if there are deepere layers revursiveley
        # I will use block list.
        if block["deepLevel"] == 0:
            block["index"] = index_0_deep
            blocks_0_deep.append(block)
            index_0_deep += 1

    ###################################################
    ###################################################
    # print(indexed_feaDict_wthout_blocks.values())
    openingEl, closingEl = ("[", "]")
    bracketPairs = findNestedPairs(feaList, openingEl, closingEl)
    declaredclasses = []
    subRules = []
    posRules = []
    for i in indexed_feaDict_wthout_blocks:
        element = indexed_feaDict_wthout_blocks[i]

        # DECLARED CLASSES #
        ####################
        ####################
        if element == openingEl:
            # Declartation
            if indexed_feaDict_wthout_blocks[i - 1] == "=":
                opening_Index = i
                closing_index = _getCorrespondingBraceIndex(i, bracketPairs)
                classDeclaration = {}
                classDeclaration["type"] = "declared-class"
                classDeclaration["name"] = indexed_feaDict_wthout_blocks[i - 2]
                classDeclaration["content"] = feaList[
                    opening_Index + 1:closing_index]
                classDeclaration["feaList_index_range"] = (
                    i - 2, closing_index + 2)
                declaredclasses.append(classDeclaration)

        #########
        # RULES #
        #########
        if element == "sub":
            sub_operator_index = None
            opening_Index = i
            closing_index = None

            # searching for closing index
            for j in indexed_feaDict_wthout_blocks:
                if j > i:
                    if indexed_feaDict_wthout_blocks[j] == ";":
                        closing_index = j + 1
                        break

            temp_ruleElements = feaList[opening_Index:closing_index]
            temp_ruleElements.pop(0)
            temp_ruleElements.pop(-1)

            for subOperator in ("by", "from"):
                if subOperator in temp_ruleElements:
                    sub_operator_index = temp_ruleElements.index(subOperator)

            subRule = {}
            subRule["type"] = "sub-rule"
            subRule["operator"] = temp_ruleElements[sub_operator_index]
            subRule["targets"] = [el for el in temp_ruleElements[
                :sub_operator_index] if el != "[" and el != "]"]
            subRule["replacements"] = [el for el in temp_ruleElements[
                sub_operator_index + 1:] if el != "[" and el != "]"]
            subRule["feaList_index_range"] = (opening_Index, closing_index)
            subRules.append(subRule)

        elif element == "pos":
            # searching for closing index
            opening_Index = i
            closing_index = None
            for j in indexed_feaDict_wthout_blocks:
                if j > i:
                    if indexed_feaDict_wthout_blocks[j] == ";":
                        closing_index = j + 1
                        break

            values = []
            value_opening = None
            for i, el in enumerate(feaList[opening_Index:closing_index]):
                if "<" and ">" in feaList[opening_Index:closing_index]:
                    if el == ">":
                        break

                    if el == "<":
                        value_opening = i

                    if value_opening:
                        if i > value_opening:
                            values.append(el)
                else:
                    if "-" in el or el[0] in strdigits:
                        values = [el]

            posRule = {}
            posRule["type"] = "pos-rule"
            posRule["values"] = {}
            posRule["feaList_index_range"] = (opening_Index, closing_index)
            if len(values) == 4:
                posRule["values"]["xPlacement"], posRule["values"]["yPlacement"], posRule[
                    "values"]["xAdvance"], posRule["values"]["yAdvance"] = values
            elif len(values) == 1:
                posRule["values"]["xPlacement"] = values[0]

            # print(feaList[opening_Index:closing_index])
            pre_targets = []
            for i, el in enumerate(feaList[opening_Index + 1:closing_index]):
                if el == "<" or el[0] == "-" or el[0] in strdigits:
                    break
                pre_targets.append(el)

            bracesDict = findNestedPairs(pre_targets, "[", "]")
            braceIndexes = []
            pre_targets_wtho_targets = []
            for braceIndex in bracesDict:
                braceIndexes.append(braceIndex)
            if len(braceIndexes) == 2:
                pre_targets_wtho_targets = [i for i in pre_targets if i not in pre_targets[
                    braceIndexes[0]:braceIndexes[1] + 1]]

            elif len(braceIndexes) == 4:
                pre_targets_wtho_targets = [i for i in pre_targets if i not in pre_targets[
                    braceIndexes[0]:braceIndexes[1] + 1]]
                pre_targets_wtho_targets = [i for i in pre_targets_wtho_targets if i not in pre_targets[
                    braceIndexes[2]:braceIndexes[3] + 1]]

            if len(bracesDict.keys()) == 4 or len(pre_targets_wtho_targets) > 0 or len(pre_targets) == 2:
                posRule["rule-type"] = 2
                if len(bracesDict.keys()) == 4:
                    posRule["targets"] = [
                        pre_targets[braceIndexes[0] + 1:braceIndexes[1]],
                        pre_targets[braceIndexes[2] + 1:braceIndexes[3]]
                    ]
                elif len(bracesDict.keys()) == 2:
                    if pre_targets[0] == "[":
                        posRule["targets"] = [
                            pre_targets[braceIndexes[0] + 1:braceIndexes[1]],
                            pre_targets_wtho_targets
                        ]
                    else:
                        posRule["targets"] = [
                            pre_targets_wtho_targets,
                            pre_targets[braceIndexes[0] + 1:braceIndexes[1]]
                        ]

                else:
                    posRule["targets"] = [[pre_targets[0]], [pre_targets[1]]]

            elif len(bracesDict.keys()) == 2 and len(pre_targets_wtho_targets) == 0 or len(pre_targets) == 1:
                posRule["rule-type"] = 1
                if len(bracesDict.keys()) == 2:
                    posRule["targets"] = [pre_targets[
                        braceIndexes[0] + 1:braceIndexes[1]]]
                else:
                    posRule["targets"] = [pre_targets]
            posRules.append(posRule)

    for b in blocks_0_deep:  # test
        print(b)  # test
    for sr in subRules:
        print(sr)
    for pr in posRules:
        print(pr)
    for c in declaredclasses:
        print(c)

    return blocks

if __name__ == "__main__":
    currDir = os.path.dirname(os.path.abspath(__file__))
    feaPath = currDir + "/supersimple.fea"
    # feaPath = currDir + "/example.fea"
    feaList = stripFea(feaPath)
    print(feaList)
    # bl = getBlocks(feaList)
