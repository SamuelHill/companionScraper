from abc import ABCMeta

class Writer(metaclass=ABCMeta):
	def start(self):
		print('Starting new level')
	def end(self):
		print('Concluding current level')
	def startCluster(self):
		print('Starting new cluster')
	def header(self, item_name):
		print('Get cluster header', item_name)
	def endCluster(self):
		print('Concluding current cluster')
	def entry(self, item_name, content):
		print('Append Entry',item_name,':',content)
	def text(self, content):
		print('Append Text',content)
	def output(self):
		return 'Unimplemented writer output function'
	def clear(self):
		print('Cleared')

class JSONWriter(Writer):
	def __init__(self):
		self.outputStr = ''
		self.current_level = 0
		self.max_level = 1
	def start(self):
		if self.current_level < self.max_level:
			self.current_level+=1
		else:
			self.outputStr += ','
		self.max_level+=1
		self.outputStr += '{'
	def end(self):
		self.max_level-=1
		if self.current_level > self.max_level:
			self.current_level-=1
		self.outputStr += '}'
	def startCluster(self):
		if self.current_level < self.max_level:
			self.current_level+=1
		else:
			self.outputStr += ','
		self.max_level+=1
		self.outputStr += '['
	def header(self, item_name):
		if self.current_level < self.max_level:
			self.current_level+=1
		else:
			self.outputStr += ','
		self.max_level+=1
		self.outputStr += '"' +item_name + '":'
	def endCluster(self):
		self.max_level-=1
		if self.current_level > self.max_level:
			self.current_level-=1
		self.outputStr += ']'
	def entry(self, item_name, content):
		if self.current_level < self.max_level:
			self.current_level+=1
		else:
			self.outputStr += ','
		self.outputStr += '"'+item_name + '":"'+content+'"'
	def text(self, content):
		if self.current_level < self.max_level:
			self.current_level+=1
		else:
			self.outputStr += ','
		self.outputStr += '"'+content+'"'
	def output(self):
		return self.outputStr
	def clear(self):
		self.outputStr = ''
		self.current_level = 0
		self.max_level = 1

Writer.register(JSONWriter)

def main():
	c = JSONWriter()
	c.start()
	c.end()
	print(c.output())
	c.clear()
	c.start()
	c.entry('a','b')
	c.entry('a2','b2')
	c.header('s')
	c.startCluster()
	c.text('wel')
	c.text('stf')
	c.endCluster()
	c.start()
	c.header('s')
	c.startCluster()
	c.text('wel')
	c.text('stf')
	c.endCluster()
	c.header('s')
	c.startCluster()
	c.text('wel')
	c.text('stf')
	c.endCluster()
	c.end()
	c.header('s')
	c.startCluster()
	c.text('wel')
	c.text('stf')
	c.endCluster()
	c.start()
	c.start()
	c.start()
	c.end()
	c.end()
	c.header('s')
	c.start()
	c.entry('a','b')
	c.end()
	c.end()
	c.end()
	print(c.output())
	c.clear()

if __name__=='__main__':
	main()