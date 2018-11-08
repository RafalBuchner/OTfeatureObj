import os
'''
@ = [ ] { } ;
languagesystem
feature lookup 
pos sub by 
'''
special_Characters = ( "[", "]", "{", "}", ";" )
special_expressions = ( "languagesystem", "feature", "lookup", "pos", "sub", "by" )

def stripFea(path):
	assert path.split('/')[-1].split('.')[-1] == "fea", "passed file is not a OT-feature file"
	file = open(path,"r") 
	fea_text =  file.read()
	fea_text_list_temp = []

	for element in fea_text.split(' '):
		if len(element) > 0:
			for sub_element in element.partition('\n'):
				if sub_element != '':
					fea_text_list_temp.append(sub_element)

	fea_text_list = []
	for element in fea_text_list_temp:
		skip = False # flow control
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
	
	return fea_text_list

currDir = os.path.dirname(os.path.abspath(__file__))
feaPath = currDir + "/example.fea"

print("*******")
print("*******")
print("*******")
print( stripFea(feaPath) )
print( )
for element in stripFea(feaPath):
	print(" "+element, end="")
print()
