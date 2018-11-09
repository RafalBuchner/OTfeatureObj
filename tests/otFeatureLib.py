
class FEA_Doc(object):
    '''
    FEA_Doc:
            Base object, that represents feature code
	
	USAGE:
    >>> feaDoc = FEA_Doc()
    >>> print(feaDoc)
    <FEA_Doc Object>
    '''

    def __init__(self):
        pass

    def loadFeaFile(self, path):
        pass

    def saveFeaFile(self, path):
        pass

    def __repr__(self):
        return f"<FEA_Doc Object>"


class FEA_Lookup(object):
    pass


class FEA_Feature(object):
    pass


class FEA_Class(object):

    def __init__(self, name):
        self.name = name


class FEA_Rule(object):
	'''
		type = "pos" or "sub"
    '''
    def __init__(self, type):
        
        self.type = type
        self.target = None
        if type == "pos":
            self.target2 = None
            self.valueRecord = None
        elif type == "sub":
            self.replacement = None

if __name__ == "__main__":
    import doctest
    doctest.testmod()
