
import operator as op 

import numpy as np
from numpy.linalg import linalg as la

import math as m

from node import Node

from OpenGL.GL import *
from OpenGL.GLU import *

class Cursor(Node) :

	def __init__( self , geom , node ) :
		Node.__init__( self , geom )

		self.node = node
	def move_axis( self , dist , axis ) :
		''' translate cursor in self.node space '''

		axis = np.array( axis )
		axis = axis / la.norm( axis )
		axis*= dist

		return self.move_vec( axis )

	def move_vec( self , vec ) :
		vec = np.array(vec)
		vec = vec * 0.001
		vec.resize( 4 , refcheck=False )
		vec = la.dot(la.transpose( la.inv( np.reshape(self.node.m,(4,4)) )) , vec )
		self.translate( *vec[0:3] )

		return vec[0:3]

