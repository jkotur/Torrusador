
import operator as op 

import numpy as np
from numpy import linalg as la

import math as m

from node import Node

from OpenGL.GL import *
from OpenGL.GLU import *

class Camera(Node) :

	def __init__( self ) :
		Node.__init__( self )

		self.p = self.la = self.lb = self.m

	def refresh( self ) :
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glLoadIdentity()
#        glMultMatrixf( self.p  )
		glMultMatrixf( self.la )
		glMultMatrixf( self.lb )
		self.m = glGetFloatv(GL_MODELVIEW_MATRIX)
		glPopMatrix()

	def rot( self , ax , ay ) :
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glLoadIdentity()
		glRotatef( ax , 0, 1, 0 )
		glRotatef( ay , 1, 0, 0 )
		glMultMatrixf( self.m )
		self.m = glGetFloatv(GL_MODELVIEW_MATRIX)
		glPopMatrix()

	def move( self , fwd , right , up ) :
		self.m[3][2] += fwd
		self.m[3][1] += up
		self.m[3][0] += right

	def lookat( self , eye , center , up ) :
		look  = map( op.sub , center , eye )
		right = np.cross( look  , up   )
		up    = np.cross( right , look )

		# normalize
		look  = look  / la.norm(look)
		right = right / la.norm(right)
		up    = up    / la.norm(up)

		a = [ [ right[0] , up[0] , -look[0] , 0 ] ,
			  [ right[1] , up[1] , -look[1] , 0 ] ,
			  [ right[2] , up[2] , -look[2] , 0 ] ,
			  [   0      ,  0    ,    0     , 1 ] ]
		b = [ [   1     ,   0     ,   0     , 0 ] ,
			  [   0     ,   1     ,   0     , 0 ] ,
			  [   0     ,   0     ,   1     , 0 ] ,
			  [ -eye[0] , -eye[1] , -eye[2] , 1 ] ]
		self.la = a
		self.lb = b

		np.concatenate(tuple(self.la))
		np.concatenate(tuple(self.lb))

		self.refresh()

