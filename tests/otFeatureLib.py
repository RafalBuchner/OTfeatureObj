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
        if path:
            self.loadFeaFile(path) 
        else: 
            self.content = []
        self.globalClassesNames = [] ### WIP ### Think how to implement it on 0 level, propably in loadFeaFile(), but how????

    @staticmethod
    def _nestLevel(el,count):
        def _deep(el,count):
            if hasattr(el, "content"):
                count += 1
                for sub in el.content:
                    # print("\t", sub, count)
                    sub.nestLevel = count
                    _deep(sub,count)

        if hasattr(el, "parent"):
            # print(el, count)
            el.nestLevel = count
            _deep(el,count)
             
        else:
            return_count = count
            count = 0
            return return_count

    def loadFeaFile(self, path):
        feaDict = readFeaFile(path)
        self.content = self.readFeaContent(self,feaDict)

        for el in self.content:
            self._nestLevel(el,0)


    def readFeaContent(self,parent, FEAcontent):
        content = {}
        for el_type in FEAcontent:

            if el_type == "expressions":
                for element in FEAcontent[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    one_line_expression = FEA_OneLineExpression(name=element["type"],args=element["arguments"])
                    one_line_expression.parent = parent
                    content[feaList_index] = one_line_expression

            elif el_type == "declaredclasses":
                for element in FEAcontent[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    declaredClass = FEA_Class(element["content"],element["name"])
                    declaredClass.parent = parent
                    content[feaList_index] = declaredClass

            elif el_type == "subRules":
                for element in FEAcontent[el_type]:
                    feaList_index = element["feaList_index_range"][0]

                    lookupType, targets, values, operator, isContextual, contextualSequence = (
                            element["rule-type"],
                            element["targets"],
                            element["replacements"],
                            element["operator"],
                            element["contextual"],
                            element["contextual-sequence"],
                        )

                    subRule = FEA_Rule(element["type"].split("-")[0])
                    subRule._initSUB(lookupType, targets, values, operator, isContextual, contextualSequence)
                    subRule.parent = parent
                    content[feaList_index] = subRule

            elif el_type == "posRules":
                for element in FEAcontent[el_type]:
                    feaList_index = element["feaList_index_range"][0]
                    lookupType, targets, values, operator, isContextual, contextualSequence = (
                            element["rule-type"],
                            element["targets"],
                            element["values"],
                            element["operator"],
                            element["contextual"],
                            element["contextual-sequence"],
                        )
                    # for value_key in values:
                    #     values[value_key] = int(values[value_key])
                    posRule = FEA_Rule(element["type"].split("-")[0])
                    posRule._initPOS(lookupType, targets, values, operator, isContextual, contextualSequence)
                    posRule.parent = parent
                    content[feaList_index] = posRule

            elif el_type == "blocks":
                for element in FEAcontent[el_type]:

                    """   type   name   deepLevel   index   feaList_index_range   content   max_deep   type   name   deepLevel   index   feaList_index_range   content   max_deep
                    """
                    feaList_index = element["feaList_index_range"][0]
                    blockType = element["type"].split("-")[0]
                    blockName = element["name"]
                    # blockContent = element["content"] ###WIP
                    block = FEA_Block(blockType,blockName)
                    block.content = self.readFeaContent(block,element["content"]) ###WIP
                    block.parent = parent
                    content[feaList_index] = block
            
        ### changing order to the right one
        main_content = []
        for i in sorted(content.keys(), key=int):
            main_content.append(content[i])
        
        return main_content

    def add(self, item):
        item.parent = self
        self.content.append(item)
        for el in self.content:
            el.nestLevel = self._nestLevel(el,0)


    def saveFeaFile(self, path):
        for element in self.content:
            print(element)

    def __repr__(self):
        return "<FEA_Doc Object>"

class FEA_BaseElement(object):
    def __init__(self):
        self.parent = None
        self.nestLevel = None
    def getStr(self):
        return "### FEA_BaseElement"

    def _representGlyphSequence(self, glyphList, openClose=("[","]")):
        targets = ""
        openingChar,closingChar = openClose
        for i,arg in enumerate(glyphList):
            if isinstance(arg, int):
                arg = str(arg)
            if i != 0 and arg != "'":
                targets += " "
            if isinstance(arg, list):
                for i, sub_arg in enumerate(arg):
                    if i == 0:
                        targets += openingChar

                    if i!= 0:
                        targets += " "
                    targets += sub_arg
                    
                    if i == len(arg)-1:
                        targets += closingChar
            else:
                targets += arg
        return targets

class FEA_Comment(FEA_BaseElement):
    def __init__(self, comment_str=None):
        super(FEA_BaseElement, self).__init__()
        self.comment_str = comment_str

    def setComment(self, comment_str):
        self.comment_str = comment_str

    def getStr(self):
        return "# ",self.comment_str

class FEA_OneLineExpression(FEA_BaseElement):
    """
        FEATURE CODE:
        -----------------------
        <name> <args> ;
        -----------------------
    """
    def __init__(self, name,args=None):
        super(FEA_BaseElement, self).__init__()
        self.name = name
        self.args = args if args else None
    def __repr__(self):
        return "<FEA_OnLineExpression Object name:-{}->".format(self.name)
    def getStr(self):
        args = ""
        for i,arg in enumerate(self.args):
            if isinstance(self.args, list):
                if i != 0:
                    args += " "

            args += arg
        return "{} {};".format(self.name, args)

class FEA_Class(FEA_BaseElement):
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
        super(FEA_BaseElement, self).__init__()
        self.name = name if name else None
        if "@" in name:
            self.name = name[1:]
        self.args = args

    def __repr__(self):
        if self.name:
            return "<FEA_Class Object name:-@{}->".format(self.name)
        else:
            return "<FEA_Class Object <not pre-declared>>"

    def getStr(self):
        content = ""
        for i,arg in enumerate(self.args):
            if i != 0:
                content += " "
            content += arg

        if self.name:
            return "@{} = [{}];".format(self.name, content)
        else:
            return "[{}]".format(self.name, content)

class FEA_Rule(FEA_BaseElement):
    """
        prefix = \"pos\" or \"sub\"
    """
    def __init__(self, prefix=None, lookupType=0, targets=None, values=None, operator=None, isContextual=False, contextualSequence=[]):
        super(FEA_BaseElement, self).__init__()
        self.prefix = prefix
        self.target = None
        if prefix == "pos":
            self._initPOS(lookupType, targets, values, operator, isContextual, contextualSequence)
        elif prefix == "sub":
            self._initSUB(lookupType, targets, values, operator, isContextual, contextualSequence)
            
    def getStr(self):
        if not self.isContextual:
            targets = self._representGlyphSequence(self.targets)
        else:
            targets = self._representGlyphSequence(self.contextualSequence)

        if self.prefix == "sub" or self.prefix == "substitute":
            
            replacements = self._representGlyphSequence(self.replacements)

            if self.operator != "ignore":
                # SUB LookupTypes 1, 2, 3, 4
                return "{} {} {} {};".format(self.prefix, targets,self.operator,replacements , )
            else:
                return "{} {} {};".format(self.operator, self.prefix, targets, )

        if self.prefix == "pos" or self.prefix == "position":
            if self.operator != "ignore":
                # POS LookupTypes 2
                values = self._representGlyphSequence(self.values)
                if len(self.values) > 1:
                    # POS LookupTypes 1
                    values = "<{}>".format(values)
                return "{} {} {};".format(self.prefix, targets, values, )
            else:
                # ignore
                return "{} {} {};".format(self.operator, self.prefix, targets, )
        

    def _initPOS(self,lookupType, targets, values, operator=None, isContextual=False, contextualSequence=[]):
        ###WIP
        self.set_targets(targets)
        self.set_values(values)
        self.set_operator(operator)
        self.set_isContextual(isContextual,contextualSequence)
        self.set_lookupType(lookupType) ### ASSERTION? lookupType == 1 and len(targets) == 1 or lookupType == 2 and len(targets) == 2 ?
    
    def _initSUB(self,lookupType, targets, replacements, operator, isContextual=False, contextualSequence=[]):
        ###WIP
        self.set_targets(targets)
        self.set_replacements(replacements)
        self.set_operator(operator)
        self.set_isContextual(isContextual,contextualSequence)
        self.set_lookupType(lookupType) ### ASSERTION? 

    def set_lookupType(self, lookupType):
        #### needs contextual inplementation
        self.lookupType = lookupType

    def set_values(self,values):
        self.values = values
        self.replacements = None
        self.prefix = "pos"

    def set_replacements(self,replacements):
        self.replacements = replacements
        self.values = None
        self.prefix = "sub"

    def set_isContextual(self,isContextual,contextualSequence):
        self.isContextual = isContextual
        self.contextualSequence = contextualSequence

    def set_operator(self,operator):
        self.operator = operator
        if self.operator == "ignore":
            self.isIgnore = True
        else:
            self.isIgnore = False

    def set_targets(self, targets):
        """
            Sets targets for the rule.
            The targets should be a list with the names of the glyphs that are going to be targetted in the rule
        """

        self.targets = targets

    
    def __repr__(self):
        return "<FEA_Rule Object -G{}-LookupType-{}>".format(self.prefix.upper(), self.lookupType)

class FEA_Block(FEA_BaseElement):
    """
        FEATURE CODE:
        -----------------------
        <type> <name> {
            <content>
        } <name>;
        -----------------------
    """
    def __init__(self,blockType=None,name=None,content=None):
        super(FEA_BaseElement, self).__init__()
        self.blockType = blockType if blockType else None
        self.name = name if name else None
        self.content = content if content else []
        # print((self.content))
        # FEA_Doc.readFeaContent(FEA_Doc,self.content)

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
        item.parent = self
        self.content.append(item)

    def __repr__(self):
        return "<FEA_Block Object type:-{}- name:-{}->".format(self.blockType, self.name)

    def getStr(self):
        # print(self.content)
        if self.name:
            name = " " + self.name
        else:
            name = ""
        if self.blockType:
            blockType = self.blockType
        else:
            blockType = ""
        
        block_str = "%s%s{" % (blockType,name)
        for el in self.content:
            # In order to create proper nesting, you need to create variable isChild or method getParent
            tabs = "\t"*el.nestLevel
            block_str += "\n%s%s\n" % (tabs,el.getStr())
        block_str += "%s} %s;" % ("\t"*(el.nestLevel-1),name)

        return block_str


if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import os
    currDir = os.path.dirname(os.path.abspath(__file__))
    feaPath = currDir + "/supersimple.fea"
    
    feaDoc = FEA_Doc(feaPath)
    # LC = FEA_Class(["a", "b", "c"], "LC")
    # SC = FEA_Class(["a.smcp", "b.smcp", "c.smcp"], "SC")
    # smcpFea = FEA_Block("feature","smcp")
    # smcpLC_SC = FEA_Rule("sub", 1, ["@LC"], ["@SC"], "by")
    # smcpFea.add(smcpLC_SC)
    # feaDoc.add(LC)
    # feaDoc.add(SC)
    # feaDoc.add(smcpFea)
    
    


    for el in feaDoc.content:
        print(el.getStr())

        # print(el.parent)
        # count = 0

