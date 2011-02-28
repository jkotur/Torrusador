
import operator as op 

import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

class Node :

	def __init__( self , geom = None ) :

		self.m = [ [1,0,0,0] , [0,1,0,0] , [0,0,1,0] , [0,0,0,1] ]
		self.childs = []
		self.geom = geom 

	def add_child( self , child ) :
		if child not in self.childs :
			self.childs.append( child )

	def del_child( self , child ) :
		self.childs.remove( child )

	def draw( self ) :
		if self.geom :
			self.geom.draw()

	def multmatrix( self ) :
		glMultMatrixf( np.concatenate(tuple(self.m)) )

	def translate( self , x , y , z ) :
		pass

	def rotate( self , a , x , y , z ) :
		pass

	def scale( self , x , y , z ) :
		pass

