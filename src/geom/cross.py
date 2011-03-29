

from dummy import *

class Cross( Dummy ) :
	
	def __init__( self , r = 0.1) :
		self.r = r
		Dummy.__init__(self)
		self.settype( GL_LINES )

	def geometry( self ) :
		return [ -self.r,0,0 , self.r,0,0 , 0,-self.r,0 , 0,self.r,0 , 0,0,-self.r , 0,0,self.r ]

