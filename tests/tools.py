import re

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
