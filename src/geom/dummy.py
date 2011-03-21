
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
		self.P0 = -1

		self.type = GL_LINES

	def __del__( self ) :
#        glDeleteBuffers( 1 , self.bid )
		pass

	def geometry( self ) :
		return []

	def settype( self , type ) :
		self.type = type

	def refresh( self ) :
		self.mode = 0

	def draw( self ) :
#        self.draw_by_hand()
		self.draw_with_ogl()

	def draw_with_ogl( self ):
		if self.mode == 0 :
			self.geom = np.array(self.geometry())
			self.count = len(self.geom)/3

#            print
#            print self.geom , len(self.geom) , self.count
#            print

#            glBindBuffer(GL_ARRAY_BUFFER,self.bid)
#            glBufferData(GL_ARRAY_BUFFER,self.geom,GL_DYNAMIC_DRAW)
#            glBindBuffer(GL_ARRAY_BUFFER,0)
			self.mode = 1

		glEnableClientState(GL_VERTEX_ARRAY)
#        glBindBuffer(GL_ARRAY_BUFFER,self.bid)
		glVertexPointer(3,GL_FLOAT,0,self.geom)
		glDrawArrays(self.type,0,self.count)
#        glBindBuffer(GL_ARRAY_BUFFER,0)
		glDisableClientState(GL_VERTEX_ARRAY)

	def draw_by_hand( self ) :
		if self.type == GL_LINE_STRIP :
			self.draw_lines()
		elif self.type == GL_POINTS :
			self.draw_points()


	def draw_lines( self ) :
		if self.mode == 0 :
			self.geom = self.geometry()
			self.geom = [ np.array(self.geom[i:i+3]+[1]) for i in range(0,len(self.geom),3) ]
			self.geom = reduce( lambda l , v : l+[v,v] , self.geom , [] )
			self.geom.pop(0)
			self.geom.pop()
			self.count = len(self.geom)

			self.mode = 1

		p = glGetFloatv(GL_TRANSPOSE_PROJECTION_MATRIX)
		m = glGetFloatv(GL_TRANSPOSE_MODELVIEW_MATRIX)

		ng = []
		for i in range(0,len(self.geom),2) :
			v = la.dot(m,self.geom[i  ])
			w = la.dot(m,self.geom[i+1])

			def multlistcut( mat , vec ) :
				vec = la.dot(mat,vec)
				vec/=vec[3]
				return list(vec)[0:3]

			if v[2] < self.P0 and w[2] < self.P0 :
				ng += multlistcut(p,v)
				ng += multlistcut(p,w)
			elif v[2] < self.P0 and w[2] >=self.P0 :
				s = (w[2] - v[2])/(self.P0-v[2])
				ng += multlistcut(p,v)
				ng += multlistcut(p,(w-v)/s + v)
			elif v[2] >=self.P0 and w[2] < self.P0 :
				s = (v[2] - w[2])/(self.P0-w[2])
				ng += multlistcut(p,(v-w)/s + w)
				ng += multlistcut(p,w)


		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		glOrtho( -1 , 1 , -1 , 1 , -100 , 100 )
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glLoadIdentity()

		glEnableClientState(GL_VERTEX_ARRAY)
		glVertexPointer(3,GL_FLOAT,0,ng)
		glDrawArrays(GL_LINES,0,len(ng)/3)
		glDisableClientState(GL_VERTEX_ARRAY)

		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glPopMatrix()

