
import operator as op 

import numpy as np
import math as m

from OpenGL.GL import *
from OpenGL.GLU import *

class Node( set ) :

	def __init__( self , geom = None ) :
		set.__init__( self )

		self.loadIdentity()
		self.geom = geom 
		self.pos  = np.array((0.0,0.0,0.0))

	def __hash__( self ) :
		return id(self)

	def __repr__( self ) :
		return set.__repr__(self) + " -- " + str(self.geom)

	def __nonzero__( self ) :
		return True

	def get_pos( self ) :
		return self.pos

	def loadIdentity( self ) :
		self.m = [ [1,0,0,0] , [0,1,0,0] , [0,0,1,0] , [0,0,0,1] ]
		self.m = np.concatenate(tuple(self.m)) 

	def add_child( self , child ) :
		self.add( child )

	def del_child( self , child ) :
		self.remove( child )

	def draw( self ) :
		if self.geom :
			self.geom.draw()

	def multmatrix( self ) :
		glMultMatrixf( self.m )

	def translate( self , x , y , z ) :
		self._mulandget( [ 1,0,0,0 , 0,1,0,0 , 0,0,1,0 , x,y,z,1 ] )

		self.pos += np.array((x,y,z))

	def rotate( self , a , x , y , z ) :
		c = m.cos( a )
		s = m.sin( a )
		xx = x*x
		yy = y*y
		zz = z*z
		r = [  xx+(1-xx)*c  , x*y*(1-c)+z*s , x*z*(1-c)-y*s , 0 , 
			  x*y*(1-c)-z*s ,  yy+(1-yy)*c  , y*z*(1-c)+x*s , 0 ,
			  x*z*(1-c)+y*s , y*z*(1-c)-x*s ,  zz+(1-zz)*c  , 0 ,
					0       ,       0       ,       0       , 1 ]
		self._mulandget( r )

	def scale( self , x , y , z ) :
		self._mulandget( [ x,0,0,0 , 0,y,0,0 , 0,0,z,0 , 0,0,0,1 ] )

	def _mulandget( self , m , inverted = False ) :
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		if not inverted :
			glLoadMatrixf( m )
			glMultMatrixf( self.m )
		else :
			glLoadMatrixf( self.m )
			glMultMatrixf( m )
		self.m = glGetFloatv(GL_MODELVIEW_MATRIX)
		glPopMatrix()

