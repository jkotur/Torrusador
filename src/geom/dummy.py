
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

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
		if self.mode == 0 :
			self.geom = numpy.array(self.geometry())
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

