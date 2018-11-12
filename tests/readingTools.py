import os
import copy
from tools import findNestedPairs, wrapBraces

special_Characters = ("[", "]", "{", "}", "<", ">", ";", "#", "'",)
special_Characters_opening = ("[", "{", "<",)
special_Characters_closing = ("]", "}", ">",)
strdigits = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0",)

"""
 TODO:
 APPLY 
 include(PATH);
"""
def getFeaText(path):
    """
        imports fea_text from the path
    """
    assert path.split(
        '/')[-1].split('.')[-1] == "fea", "passed file is not a OT-feature file"
    file = open(path, "r")
    fea_text = file.read()
    return fea_text


def getFeaList(fea_text):
    """
        fea_text - string written in OPENTYPE FEATURE FILE SYNTAX
        https://www.adobe.com/devnet/opentype/afdko/topic_feature_file_syntax.html
        [ THIS IS BETA VERSION: CURRENTLY THE IMPLEMENTATION COVERS SYNTAX COVERED BY TAL LEMING IN OPENTYPE COOKBOOK (http://opentypecookbook.com/)]
        
        Divides fea_text into semiotic elements of the syntax. 
        It ignores comments.


        USAGE
        >>> fea_text = '''
        ... languagesystem DFLT dflt;
        ... languagesystem latn dflt;
        ...
        ... # Comment
        ... @lowercase = [a    b    c];
        ... @smallcaps = [A.sc B.sc C.sc];
        ...
        ... feature smcp {
        ...     sub @lowercase by @smallcaps;
        ... } smcp;
        ...
        ... feature kern {
        ...     pos V A -50;
        ... } kern;
        ... '''
        >>> feaList = getFeaList(fea_text)
        >>> print(feaList)
        ['languagesystem', 'DFLT', 'dflt', ';', 'languagesystem', 'latn', 'dflt', ';', '@lowercase', '=', '[', 'a', 'b', 'c', ']', ';', '@smallcaps', '=', '[', 'A.sc', 'B.sc', 'C.sc', ']', ';', 'feature', 'smcp', '{', 'sub', '@lowercase', 'by', '@smallcaps', ';', '}', 'smcp', ';', 'feature', 'kern', '{', 'pos', 'V', 'A', '-50', ';', '}', 'kern', ';']
    """
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
                opening_index = i
                closing_index = _getCorrespondingBraceIndex(i, nestedPairs)
                block_descrpition["type"] = f"{feaList[i - 2]}-block"
                block_descrpition["name"] = feaList[i - 1]
                block_descrpition["deepLevel"] = nestedPairs[i][2]
                block_descrpition["index"] = block_index
                block_descrpition["feaList_index_range"] = (
                    opening_index - 2, closing_index + 3)  # range of global indexes
                block_descrpition["content"] = feaList[
                    opening_index + 1:closing_index]
                temp_collection_deeLevels = [0]  # WIP
                start_digging = False
                for brace_index in nestedPairs:  # WIP
                    if brace_index == opening_index:
                        start_digging = True
                    elif brace_index == closing_index:
                        start_digging = False
                        break
                    if start_digging:
                        temp_collection_deeLevels.append(
                            nestedPairs[brace_index][2])
                max_deep = max(temp_collection_deeLevels)

                block_descrpition["max_deep"] = max_deep  # WIP
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
    expressions = []
    for j, i in enumerate(indexed_feaDict_wthout_blocks):
        element = indexed_feaDict_wthout_blocks[i]

        prev_element = list(indexed_feaDict_wthout_blocks.values())[
            j - 1] if j > 0 else None

        #######################
        # SPECIAL EXPRESSIONS #
        #######################
        if element in ("languagesystem", "language", "script"):
            opening_index = i
            closing_index = None

            for j, el in enumerate(feaList):
                if el == ";" and j > opening_index:
                    closing_index = j + 1
                    break
            expression = {}
            expression["feaList_index_range"] = (opening_index, closing_index)
            expression["type"] = element
            expression["arguments"] = feaList[
                opening_index + 1:closing_index - 1]
            expressions.append(expression)

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
        # ------------------------------------------------------------------------------------------------------------------------
        # GSUB Lookups
        # ------------------------------------------------------------------------------------------------------------------------
        if element == "sub" or element == "substitute":
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

        # ------------------------------------------------------------------------------------------------------------------------
        # GPOS Lookups
        # ------------------------------------------------------------------------------------------------------------------------
        elif element == "pos" or element == "position":

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
            pre_targets_wtho_braces = []
            for braceIndex in bracesDict:
                braceIndexes.append(braceIndex)

            if len(wrapBraces(pre_targets, ("[", "]"))) == 1:
                posRule["rule-type"] = 1
            elif len(wrapBraces(pre_targets, ("[", "]"))) == 2:
                posRule["rule-type"] = 2

            posRule["targets"] = wrapBraces(pre_targets, ("[", "]"))

            # contextual
            input_glyphs = []
            for i, el in enumerate(posRule["targets"]):
                if el == "'":
                    input_glyphs.append(posRule["targets"][i - 1])
            if len(input_glyphs) > 0:
                # that means that the rule has contextual behaviour
                posRule["contextual-sequence"] = posRule["targets"]
                posRule["targets"] = input_glyphs
                if prev_element == "ignore":
                    posRule["operator"] = "ignore"

                if len(posRule["targets"]) == 1:
                    posRule["rule-type"] = 1
                elif len(posRule["targets"]) == 2:
                    posRule["rule-type"] = 2
                posRule["sub-type"] = 8

            posRules.append(posRule)

    return {"expressions": expressions, "declaredclasses": declaredclasses, "subRules": subRules, "posRules": posRules, "blocks": blocks_0_deep}


def readFeaList(feaList):
    semanticDicts = getSemanticDicts(feaList)

    if len(semanticDicts["blocks"]) == 0:
        return semanticDicts

    for i, block in enumerate(semanticDicts["blocks"]):
        block["content"] = readFeaList(block["content"])

        if i == len(semanticDicts["blocks"]) - 1:
            return semanticDicts


def readFeaFile(feaPath):
    fea_txt = getFeaText(feaPath)
    feaList = getFeaList(fea_txt)
    feaDict = readFeaList(feaList)
    return feaDict


# if __name__ == "__main__":
#     currDir = os.path.dirname(os.path.abspath(__file__))
#     feaPath = currDir + "/example.fea"
#     feaDict = readFeaFile(feaPath)
if __name__ == "__main__":
    import doctest
    doctest.testmod()
