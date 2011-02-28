
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

	def multmatrix( self ) :
		glMultMatrixf( np.concatenate(tuple(self.p )) )
		glMultMatrixf( np.concatenate(tuple(self.la)) )
		glMultMatrixf( np.concatenate(tuple(self.lb)) )

	def projection( self , fov , aspect , near , far ) :
		f = 1.0/m.tan( fov*m.pi / 180.0 / 2.0 )
		self.p = [ [ f / aspect , 0 ,           0           ,  0 ] ,
				   [   0        , f ,           0           ,  0 ] ,
				   [   0        , 0 , float(far+near)/(near-far) , -1 ] ,
				   [   0        , 0 , 2.0*far*near/(near-far) ,  0 ] ]

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

