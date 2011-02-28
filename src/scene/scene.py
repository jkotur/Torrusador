
class Scene :
	def __init__( self , root = None ) :
		self.root = root

	def gfx_init( self ) :
		pass

	def draw( self , node = None ) :
		if not node :
			node = self.root

		node.multmatrix()
		node.draw()

		for c in node.childs :
			self.draw( c )

