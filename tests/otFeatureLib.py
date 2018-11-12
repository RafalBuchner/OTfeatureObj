from readingTools import readFeaFile

class FEA_Doc(object):
    '''
    FEA_Doc:
            Base object, that represents feature code
    
    USAGE:
    >>> feaDoc = FEA_Doc()
    >>> print(feaDoc)
    <FEA_Doc Object>
    '''

    def __init__(self, path=None):
        self. path = path if path else None
        self.content = self.loadFeaFile(path) if path else []
        self.globalClassesNames = [] ### WIP ### Think how to implement it on 0 level, propably in loadFeaFile(), but how????

    def loadFeaFile(self, path):
        feaDict = readFeaFile(path)
        content = {}
        for el_type in feaDict:
            print(el_type)
            if el_type == "expressions":
                for element in feaDict[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    one_line_expression = FEA_OnLineExpression(name=element["type"],args=element["arguments"])
                    content[feaList_index] = one_line_expression

            elif el_type == "declaredclasses":
                for element in feaDict[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    declaredClass = FEA_Class(element["content"],element["name"])
                    content[feaList_index] = declaredClass

            elif el_type == "subRules":
                for element in feaDict[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    pass

            elif el_type == "posRules":
                for element in feaDict[el_type]:
                    print(element)
                    feaList_index = element["feaList_index_range"][0]
                    pass

            elif el_type == "blocks":
                for element in feaDict[el_type]:

                    """   type   name   deepLevel   index   feaList_index_range   content   max_deep   type   name   deepLevel   index   feaList_index_range   content   max_deep
                    """
                    feaList_index = element["feaList_index_range"][0]
                    blockType = element["type"].split("-")[0]
                    blockName = element["name"]
                    blockContent = element["content"]
                    block = FEA_Block(blockType,blockName,blockContent)
                    content[feaList_index] = block
        
        ### changing order to the right one
        main_content = []
        for i in sorted(content.keys(), key=int):
            main_content.append(content[i])
        print(main_content)

    def saveFeaFile(self, path):
        pass

    def __repr__(self):
        return f"<FEA_Doc Object>"




class FEA_OnLineExpression(object):
    """
        FEATURE CODE:
        -----------------------
        <name> <args> ;
        -----------------------
    """
    def __init__(self, name,args=None):
        self.name = name
        self.args = args if args else None
    def __repr__(self):
        return f"<FEA_OnLineExpression Object>"

class FEA_Class(object):
    """
        FEATURE CODE:
        -----------------------
        @<name> = [ <args> ];
        -----------------------
        or without declaration
        -----------------------
        [ <args> ]
        -----------------------
    """
    def __init__(self, args, name=None):
        self.name = name if name else None
        self.args = args

    def __repr__(self):
        return f"<FEA_Class Object>"

class FEA_Rule(object):
    """
        prefix = \"pos\" or \"sub\"
    """
    def __init__(self, prefix):
        self.type = prefix
        self.target = None
        if prefix == "pos":
            self.target2 = None
            self.valueRecord = None
        elif prefix == "sub":
            self.replacement = None

    def initPOS(lookupType, targets):
        ###WIP
        self.lookType = lookupType ### ASSERTION? lookupType == 1 and len(targets) == 1 or lookupType == 2 and len(targets) == 2 ?
        self.targets = targets

    def initSUB(lookupType, targets, replacements):
        ###WIP
        self.targets = targets
        self.replacements = replacements

    def __repr__(self):
        return f"<FEA_Rule Object>"

class FEA_Block(object):
    """
        FEATURE CODE:
        -----------------------
        <type> <name> {
            <content>
        } <name>;
        -----------------------
    """
    def __init__(self,blockType=None,name=None,content=None):
        self.blockType = blockType if blockType else None
        self.name = name if name else None
        self.content = content if content else []
        self._checkType()

    def _checkType(self):
        if self.blockType == "feature":
            self.isFeature = True
            self.isLookup = False
        elif self.blockType == "lookup":
            self.isFeature = False
            self.isLookup = True

    def setBlockType(self, blockType):
        self.blockType = blockType
        self._checkType()

    def setName(self, name):
        self.name = name

    def add(self, item):
        self.content.append(item)

    def __repr__(self):
        return f"<FEA_Block Object>"




if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import os
    currDir = os.path.dirname(os.path.abspath(__file__))
    feaPath = currDir + "/rules.fea"
    feaDoc = FEA_Doc(feaPath)
