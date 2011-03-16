
from node import Node

from OpenGL.GL import *
from OpenGL.GLU import *

class Color(Node) :

	def __init__( self , c ) :
		Node.__init__( self )

		self.set_color( c )
	
	def set_color( self , c ) :
		self.c = c

	def draw( self ) :
		glColor3f( *self.c )

		Node.draw( self )

