"""
    TODO:
        RULE-TYPE IN GSUB RULES IN GETBLOCKS()
"""

import os
import re
import copy

special_Characters = ("[", "]", "{", "}", "<", ">", ";", "#", "'",)
special_Characters_opening = ("[", "{", "<",)
special_Characters_closing = ("]", "}", ">",)

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


def getFeaText(path):
    """
        TODO: change from path to txt, the object passed shouldn't be a path, but string.
        Path declaration, and file declaration should be declared outside this function
    """
    assert path.split(
        '/')[-1].split('.')[-1] == "fea", "passed file is not a OT-feature file"
    file = open(path, "r")
    fea_text = file.read()
    return fea_text


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


def wrapBraces(char_list, braces):
    """
        Takes the list that contains sequence of characters. 
        Wraps it by given braces.

        USAGE:
        >>> char_list = [ "[", "a", "b", "c", "]", "[", "d", "e", "f", "]"]
        >>> wrapped_char_list = wrapBraces(char_list,("[","]"))
        >>> print(wrapped_char_list)
        [['a', 'b', 'c'], ['d', 'e', 'f']]
        >>> char_list = ["a","b","c"]
        >>> wrapped_char_list = wrapBraces(char_list,("[","]"))
        >>> print(wrapped_char_list)
        ['a', 'b', 'c']
        >>> char_list = ["[","a","b","]","c"]
        >>> wrapped_char_list = wrapBraces(char_list,("[","]"))
        >>> print(wrapped_char_list)
        [['a', 'b'], 'c']
        >>> char_list = ["a","[","b","c","]"]
        >>> wrapped_char_list = wrapBraces(char_list,("[","]"))
        >>> print(wrapped_char_list)
        ['a', ['b', 'c']]
    """
    opening, closing = braces
    wrapped_char_list = []
    if opening in char_list and closing in char_list:
        placeholder = ">!!~?$&~!!<"
        bracesDict = findNestedPairs(char_list, opening, closing)
        braceIndexes = [indx for indx in bracesDict]
        list_of_indexes = list(range(len(char_list)))

        wrapped_char_list_with_the_rest = []
        for i_a, i_b in zip(braceIndexes[:-1], braceIndexes[1:]):
            if len(char_list[i_a + 1:i_b]) != 0:
                if char_list[i_a] == opening and char_list[i_b] == closing:
                    wrapped_char_list.append(char_list[i_a + 1:i_b])
                    # print(list_of_indexes[i_a+1:i_b])
                    for x in range(i_a + 1, i_b):
                        for i, y in enumerate(list_of_indexes):
                            if x == y:
                                index = list_of_indexes.index(y)
                                if list_of_indexes[i - 1] != placeholder:
                                    list_of_indexes.insert(index, placeholder)
                                list_of_indexes.remove(y)

        indexing_closed_bracing = 0
        for i in list_of_indexes:
            if i != placeholder:
                el = char_list[i]
                if opening != el or closing != el:
                    # print(el)wrapped_char_list_with_the_rest
                    if closing in el:
                        # print(el)
                        el = el.replace(closing, "")
                    if len(el) > 0 and el != opening:
                        wrapped_char_list_with_the_rest.append(el)
            else:
                wrapped_char_list_with_the_rest.append(
                    wrapped_char_list[indexing_closed_bracing])
                indexing_closed_bracing += 1

        return wrapped_char_list_with_the_rest
    else:
        wrapped_char_list = char_list
        return wrapped_char_list


def getFeaList(fea_text):
    feaList = []
    temp_feaList = []

    ########################
    # ignore comments:
    ########################
    keep_adding = False
    indexes_to_remove = []
    delRange = []
    copy_fea_text = copy.deepcopy(fea_text)
    for i, el in enumerate(fea_text):
        if "#" == el:
            delRange = []
            delRange = [i]
            keep_adding = True

        if keep_adding:
            if "\n" == el:
                delRange.append(i)
                indexes_to_remove.append(delRange)
                keep_adding = False

    for fromHere, toHere in indexes_to_remove:

        fea_text = fea_text.replace(copy_fea_text[fromHere:toHere], "")

    for el in fea_text.split("\n"):
        if el != "":
            temp_feaList.append(el)

    for el in temp_feaList:
        for sub_el in el.split(" "):

            if "\t" in sub_el:
                sub_el = sub_el.replace("\t", "")
            if sub_el == "":
                continue

            if len(sub_el) > 2 and sub_el[0] in special_Characters_opening and sub_el[-1] in special_Characters_closing and ";" not in sub_el:
                # sub_el = "[glyph]"

                feaList.append(sub_el[0])
                feaList.append(sub_el[1:-1])
                feaList.append(sub_el[-1])

            elif sub_el[0] in special_Characters_opening and ";" not in sub_el:
                if len(sub_el) == 1:

                    # sub_el = [
                    feaList.append(sub_el)
                elif len(sub_el) > 1:
                    # sub_el = [name
                    feaList.append(sub_el[0])
                    feaList.append(sub_el[1:])
            elif sub_el[-1] in special_Characters_closing and ";" not in sub_el:
                if len(sub_el) == 1:

                    # sub_el = ]
                    feaList.append(sub_el)
                elif len(sub_el) > 1:
                    # sub_el = name]
                    feaList.append(sub_el[:-1])
                    feaList.append(sub_el[-1])

            elif ";" in sub_el:
                if sub_el[0] in special_Characters_opening and sub_el[-1] in special_Characters and len(sub_el) >= 4:

                    # sub_el = "[glyph];"
                    feaList.append(sub_el[0])
                    feaList.append(sub_el[1:-2])
                    feaList.append(sub_el[-2])
                    feaList.append(sub_el[-1])
                elif len(sub_el) > 1 and sub_el[0] not in special_Characters_closing and sub_el[-1] == ";":

                    if len(sub_el) > 1 and sub_el[-2] not in special_Characters_closing:
                        # sub_el = "name;"
                        feaList.append(sub_el[:-1])
                        feaList.append(sub_el[-1])
                    elif len(sub_el) > 2:
                        if sub_el[-2] in special_Characters_closing:
                            # sub_el = name];
                            feaList.append(sub_el[:-2])
                            feaList.append(sub_el[-2])
                            feaList.append(sub_el[-1])
                elif sub_el[-1] == ";" and len(sub_el) > 1:

                    if sub_el[0] in special_Characters_closing:
                        # sub_el = ];
                        feaList.append(sub_el[0])
                        feaList.append(sub_el[1])

                elif ";" in sub_el and len(sub_el) == 1:
                    # sub_el = ";"
                    feaList.append(sub_el)

            elif sub_el in special_Characters:
                feaList.append(sub_el)
            else:
                feaList.append(sub_el)

    # checing out for the contextual pointers:
    temp_feaList = []
    for i, el in enumerate(feaList):
        if "'" in el:
            for char in special_Characters_closing:
                if char in el:
                    temp_feaList.append(el[:-2])
                    temp_feaList.append(el[-2])
                    temp_feaList.append(el[-1])
                else:
                    temp_feaList.append(el[:-1])
                    temp_feaList.append(el[-1])
                break
        else:
            temp_feaList.append(el)

    feaList = temp_feaList

    return feaList


def getSemanticDicts(feaList):
    """
        Returns set of dicts
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
    def _blocks():
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

                if i >= start_Index and i < end_index:
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
        return blocks_0_deep, indexed_feaDict_wthout_blocks, blocks
    blocks_0_deep, indexed_feaDict_wthout_blocks, blocks = _blocks()

    ####################
    # FLAT EXPRESSIONS #
    ####################
    openingEl, closingEl = ("[", "]")
    bracketPairs = findNestedPairs(feaList, openingEl, closingEl)
    declaredclasses = []
    subRules = []
    posRules = []
    for j, i in enumerate(indexed_feaDict_wthout_blocks):
        element = indexed_feaDict_wthout_blocks[i]

        prev_element = list(indexed_feaDict_wthout_blocks.values())[
            j - 1] if j > 0 else None

        ####################
        # DECLARED CLASSES #
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
        if element == "sub" or element == "substitute":
            # ------------------------------------------------------------------------------------------------------------------------
            # GSUB Lookups
            # ------------------------------------------------------------------------------------------------------------------------
            """
                # GSUB Lookups
                TODO:
                    - ignore
                    - Substitutions and Positioning Based on Context
                    - make sure about the GSUB Lookup types (You should take in the consideration difference between the glyphclasses and glyph sequences)
                        (now the <GSUB l-type 1 B> can be confused with <GSUB l-type 4>

            """
            subRule = {}

            sub_operator_index = None
            opening_Index = i
            closing_index = None

            # searching for closing index
            for j in indexed_feaDict_wthout_blocks:
                if j > i:
                    if indexed_feaDict_wthout_blocks[j] == ";":
                        closing_index = j + 1
                        break

            subRule["feaList_index_range"] = (opening_Index, closing_index)
            subRule["type"] = "sub-rule"

            temp_ruleElements = feaList[opening_Index:closing_index]
            temp_ruleElements.pop(0)
            temp_ruleElements.pop(-1)

            for subOperator in ("by", "from"):
                if subOperator in temp_ruleElements:
                    sub_operator_index = temp_ruleElements.index(subOperator)
            if sub_operator_index:
                # managing the class-braces
                pre_targets = [
                    el for el in temp_ruleElements[:sub_operator_index]]
                pre_replace = [el for el in temp_ruleElements[
                    sub_operator_index + 1:]]

                subRule["operator"] = temp_ruleElements[sub_operator_index]
                subRule["targets"] = wrapBraces(pre_targets, ("[", "]"))
                subRule["replacements"] = wrapBraces(pre_replace, ("[", "]"))

                if len(subRule["targets"]) == len(subRule["replacements"]) and subRule["operator"] == "by":
                    # Replace One With One - GSUB LOOKTYPE 1
                    subRule["rule-type"] = 1

                elif len(subRule["targets"]) < len(subRule["replacements"]) and subRule["operator"] == "by":
                    # Replace One With Many - GSUB LOOKTYPE 2
                    subRule["rule-type"] = 2

                elif len(subRule["targets"]) == len(subRule["replacements"]) and subRule["operator"] == "from":
                    # Replace One From Many - GSUB LOOKTYPE 3
                    subRule["rule-type"] = 3

                elif len(subRule["targets"]) > len(subRule["replacements"]) and subRule["operator"] == "by":
                    # Replace Many With One - GSUB LOOKTYPE 4
                    subRule["rule-type"] = 4

                if special_Characters[-1] in temp_ruleElements:
                    input_glyphs = []
                    subRule["contextual-sequence"] = subRule["targets"]
                    subRule["targets"] = wrapBraces(
                        subRule["targets"], ("[", "]"))
                    for i, el in enumerate(subRule["targets"]):
                        if el == "'":
                            input_glyphs.append(subRule["targets"][i - 1])

                            subRule["sub-rule-type"] = subRule["rule-type"]
                    subRule["rule-type"] = 6  # ?
                    subRule["targets"] = input_glyphs

            else:
                if prev_element:
                    if prev_element == "ignore":
                        subRule["operator"] = "ignore"
                        # subRule["targets"] = temp_ruleElements

                        input_glyphs = []
                        subRule[
                            "contextual-sequence"] = wrapBraces(temp_ruleElements, ("[", "]"))
                        for i, el in enumerate(subRule["contextual-sequence"]):
                            if el == "'":
                                input_glyphs.append(
                                    subRule["contextual-sequence"][i - 1])

                        subRule["rule-type"] = 6  # ?
                        subRule["targets"] = input_glyphs

            subRules.append(subRule)

        elif element == "pos" or element == "position":
            # ------------------------------------------------------------------------------------------------------------------------
            # GPOS Lookups
            # ------------------------------------------------------------------------------------------------------------------------
            """
                # GPOS Lookups
                TODO:

            """
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

            # managing the class-braces
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
            # print(posRule)
            posRules.append(posRule)
            # print(posRules)
            # break

    # for c laredclasses:
    #     print(c)in dec
    # for b in blocks_0_deep:
    #     print(b)
        # print(feaList[b['feaList_index_range'][0]:b['feaList_index_range'][1]])
    # for sr in subRules:
    #     print(sr)
    #     print(sr["rule-type"])
    for pr in posRules:
        print(pr)

    return blocks

if __name__ == "__main__":
    currDir = os.path.dirname(os.path.abspath(__file__))
    feaPath = currDir + "/supersimple.fea"
    # feaPath = currDir + "/example.fea"
    fea_txt = getFeaText(feaPath)
    feaList = getFeaList(fea_txt)

    bl = getSemanticDicts(feaList)
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()
