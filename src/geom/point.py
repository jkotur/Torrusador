
from dummy import *

class Point( Dummy ) :
	
	def __init__( self ) :
		Dummy.__init__(self)
		self.settype( GL_POINTS )

	def geometry( self ) :
		return [ 0,0,0 ]

