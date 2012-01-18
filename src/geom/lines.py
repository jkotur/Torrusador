
from dummy import *

class Lines( Dummy ) :
	def __init__( self ) :
		Dummy.__init__(self)
		self.settype( Dummy.SELF )

	def draw_self( self , data ) :
		for p in data :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3 , GL_FLOAT , 0 , p )
			glDrawArrays(GL_LINE_STRIP, 0, p.shape[0] )
			glDisableClientState(GL_VERTEX_ARRAY)



