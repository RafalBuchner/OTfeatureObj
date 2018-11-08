
class FEA_Doc(object):
	def __init__(self):
		pass
	def loadFeaFile(self, path):
		pass
	def saveFeaFile(self,path):
		pass

class FEA_Lookup(object):
	pass

class FEA_Feature(object):
	pass

class FEA_Class(object):
	def __init__(self, name):
		self.name = name

class FEA_Rule(object):
	def __init__(self, type):
		'''
			type = "pos" or "sub"
		'''
		self.type = type
		self.target = None
		if type == "pos":
			self.target2 = None
			self.valueRecord = None
		elif type == "sub":
			self.replacement = None
