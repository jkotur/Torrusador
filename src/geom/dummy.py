
from OpenGL.GL import *
from OpenGL.GLU import *


import numpy as np
from numpy.linalg import linalg as la

class Dummy :

	def __init__( self ) :
		self.bdata = []
		self.bid = glGenBuffers(1)
		self.bsize = 0
		self.mode = 0

	def __del__( self ) :
#        glDeleteBuffers( 1 , self.bid )
		pass

	def geometry( self ) :
		return []

	def refresh( self ) :
		self.mode = 0

	def draw( self ) :
		self.draw_by_hand()

	def draw_with_ogl( self ):
		if self.mode == 0 :
			self.geom = np.array(self.geometry())
			self.count = len(self.geom)/3

#            glBindBuffer(GL_ARRAY_BUFFER,self.bid)
#            glBufferData(GL_ARRAY_BUFFER,self.geom,GL_DYNAMIC_DRAW)
#            glBindBuffer(GL_ARRAY_BUFFER,0)
			self.mode = 1

		glEnableClientState(GL_VERTEX_ARRAY)
#        glBindBuffer(GL_ARRAY_BUFFER,self.bid)
		glVertexPointer(3,GL_FLOAT,0,self.geom)
		glDrawArrays(GL_LINE_STRIP,0,self.count)
#        glBindBuffer(GL_ARRAY_BUFFER,0)
		glDisableClientState(GL_VERTEX_ARRAY)

	def draw_by_hand( self ) :
		if self.mode == 0 :
			self.geom = self.geometry()
			self.geom = [ np.array(self.geom[i:i+3]+[1]) for i in range(0,len(self.geom),3) ]
			self.count = len(self.geom)

		m = glGetFloatv(GL_TRANSPOSE_MODELVIEW_MATRIX)

		ng = []
		for v in self.geom :
			w = la.dot(m,v)
			w/= w[3]
			ng += list(w)[0:3]

#        ng = [ ng[i:i+3] for i in range(0,len(self.geom),3) if ng[i+2] ]

		glPushMatrix()
		glLoadIdentity()
		glEnableClientState(GL_VERTEX_ARRAY)
		glVertexPointer(3,GL_FLOAT,0,ng)
		glDrawArrays(GL_LINE_STRIP,0,self.count)
		glDisableClientState(GL_VERTEX_ARRAY)
		glPopMatrix()

