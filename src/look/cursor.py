
import operator as op 

import numpy as np
from numpy.linalg import linalg as la

import math as m

from node import Node

from OpenGL.GL import *
from OpenGL.GLU import *

class Cursor(Node) :

	def __init__( self , geom ) :
		Node.__init__( self , geom )

	def get_clipping_pos( self ) :
		pos = la.dot( self.currp , la.dot( self.currmv , np.array( [0,0,0,1] ) ) )
		pos = pos / pos[3]
		return pos[:3]

	def move_axis( self , dist , axis ) :
		''' translate cursor in self.node space '''

		axis = np.array( axis )
		axis = axis / la.norm( axis )
		axis*= dist

		return self.move_vec( axis )

	def draw( self ) :
		self.currp  = glGetFloatv(GL_TRANSPOSE_PROJECTION_MATRIX)
		self.currmv = glGetFloatv(GL_TRANSPOSE_MODELVIEW_MATRIX)
		Node.draw( self )

	def move_vec( self , vec ) :
		vec = np.array(vec)
		vec = vec * 0.001
		vec.resize( 4 , refcheck=False )
		vec = la.dot( la.inv( np.reshape(self.currmv,(4,4)) ) , vec )
		self.translate( *vec[0:3] )

		return vec[0:3]

