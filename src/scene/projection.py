
import math as m

import numpy as np

from node import Node

from OpenGL.GL import *
from OpenGL.GLU import *

class Projection(Node) :

	def __init__( self ) :
		Node.__init__( self )

		self.p = self.m

	def multmatrix( self ) :
		glMatrixMode(GL_PROJECTION)
		glLoadMatrixf( self.p )
		glMatrixMode(GL_MODELVIEW)

	def perspective( self , fov , aspect , near , far ) :
		f = 1.0/m.tan( fov*m.pi / 180.0 / 2.0 )
		self.p = [ [ f / aspect , 0 ,           0                ,  0 ] ,
				   [   0        , f ,           0                ,  0 ] ,
				   [   0        , 0 , float(far+near)/(near-far) , -1 ] ,
				   [   0        , 0 ,   2.0*far*near /(near-far) ,  0 ] ]

		np.concatenate(tuple(self.p))

