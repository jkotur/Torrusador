
from curve import *

import ctypes

import sys

import numpy as np
import math as m

from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GL.EXT import *

import shaders as sh

from numpy.linalg import linalg as la

class Bspline( Curve ) :

	def __init__( self ) :
		Curve.__init__( self ) 

		self.prog = None

	def draw_self( self , data ) :
		self.geom = []
		for p in data :
			self.geom.append(p[0])
			self.geom.append(p[1])
			self.geom.append(p[2])
			self.geom.append(1)
		self.geom = np.array(self.geom,np.float32)
		self.count = len(self.geom)/4

		if self.draw_polygon :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 4, GL_FLOAT , 0 , self.geom )
			glDrawArrays(GL_LINE_STRIP, 0, self.count)
			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_points :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 4, GL_FLOAT , 0 , self.geom )
			glDrawArrays(GL_POINTS, 0, self.count)
			glDisableClientState(GL_VERTEX_ARRAY)

