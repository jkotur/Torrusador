from geom.dummy import Dummy

class MultiGeom( Dummy ) :
	def __init__( self , cont = [] ) :
		Dummy.__init__( self )

		self.geoms = cont

	def set_screen_size( self , w , h ) :
		for g in self.geoms :
			g.set_screen_size( w , h )

	def set_visibility( self , what , how ) :
		for g in self.geoms :
			g.set_visibility( what , how )

	def gfx_init( self ) :
		for g in self.geoms :
			g.gfx_init()

	def draw( self , data = None ) :
		if hasattr(data,'__iter__') :
			for i in range(len(self.geoms)) :
				self.geoms[i].draw( data[i] )
		else :
			for g in self.geoms :
				g.draw( data )

