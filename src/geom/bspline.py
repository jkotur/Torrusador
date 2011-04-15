
from curve import *

import ctypes

import sys

import numpy as np
import math as m

from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GL.EXT import *

import shaders as sh

from copy import copy

from numpy.linalg import linalg as la

def decasteljau( t , pts , knots ) :
		if len(pts) <= 0 :
			return 0

		pts = copy(pts)

		l = 0       
		while l+1 < len(knots) and knots[l+1] < t : l+= 1
		l+= 1

		n = len(pts) 
		l = 4
		n = 4

		def alpha( t , k , i ) :
			print 'kts: ' , i , i+n+1-k , knots[i] , knots[i+n+1-k]
			return (t-knots[i])/(knots[i+n-k+1]-knots[i])

		print 'nl: ' , t , n , l 

		for k in range(1,n) :
			for i in xrange(l-n+k,l) :
				a = alpha(t,k,i)
				print 'ikap: ' , i , k , a , pts 
				pts[i] = pts[i-1]*(1.0-a) + pts[i]*a
		return pts[-1]

def rekN( n , i ,  t ) :
	if n == 0 : return 1 if t >= i and t < i + 1 else 0
	n1 = rekN(n - 1, i, t)
	n2 = rekN(n - 1, i + 1, t)
	return n1 * float(t - i) / float(n) + n2 * float(i + n + 1 - t) / float(n)

NUMS = 64
	
class Bspline( Curve ) :

	def __init__( self ) :
		Curve.__init__( self ) 

		self.prog = None

		# for CPU rendering
		self.ncache = {}
		for t in np.linspace(3,4,NUMS) :
			for j in range(4) :
				self.ncache[ (j,t) ] = rekN( 3 , j , t )

		# for GPU rendering
		self.base = []
		for t in np.linspace(3,4,(256+1)/4) :
			for j in range(4) :
				self.base.append( rekN( 3 , j , t ) )
		self.base = np.array( self.base , np.float32 )

	def get_loc( self , prog , loc ) :
		location = glGetUniformLocation(prog,loc)
		if location in (None,-1): raise ValueError ('No uniform: ' + loc)
		return location                 

	def gfx_init( self ) :
		if self.is_inited : return

		try:
			self.prog = sh.compile_program("shad/bspline_base")
		except ValueError as ve:
			print "Shader compilation failed: " + str(ve)
			sys.exit(0)

		self.loc_mmv = self.get_loc(self.prog,'modelview' )
		self.loc_mp  = self.get_loc(self.prog,'projection')
		pointsid     = self.get_loc(self.prog,'points'    )
		self.l_color = self.get_loc(self.prog,'color'     )
		self.l_screen= self.get_loc(self.prog,'screen'    )
		self.l_base  = self.get_loc(self.prog,'base'      )

		self.bid  = glGenBuffers(1)
		self.btex = glGenTextures(1)

		glUseProgram( self.prog )
		glUniform1i( pointsid , 0 );
		glUniform1fv( self.l_base , 256+1 , self.base )
		glUseProgram( 0 )

		self.is_inited = True

	def draw_self( self , data ) :
		self.geom = []
		for p in data :
			self.geom.append(p[0])
			self.geom.append(p[1])
			self.geom.append(p[2])
			self.geom.append(1)
		self.geom = np.array(self.geom,np.float32)
		self.count = len(self.geom)/4

		if 0 :
			ptsx = [ p[0] for p in data ]
			ptsy = [ p[1] for p in data ]
			ptsz = [ p[2] for p in data ]

			knots = range(0,10)
			pts = []
			for i in range(0,self.count-3) :
				for t in np.linspace(3,4,NUMS) :
					x = y = z = 0
					for j in range(4) :
						n =  self.ncache[ (j,t) ]
						x += ptsx[i+j] * n
						y += ptsy[i+j] * n
						z += ptsz[i+j] * n
					pts += [ x , y , z , 1 ]
					
#                    print ptsx[i:i+4]
#                    print ptsy[i:i+4]
#                    print ptsz[i:i+4]
#                    pts += [ 
#                            decasteljau( t , ptsx[i:i+4] , knots ) ,
#                            decasteljau( t , ptsy[i:i+4] , knots ) ,
#                            decasteljau( t , ptsz[i:i+4] , knots ) ,
#                            1.0 ]

			pts = np.array(pts,np.float32)

			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 4, GL_FLOAT , 0 , pts )
			glDrawArrays(GL_LINE_STRIP, 0, int(len(pts)/4) )
			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_curve :
			nums = []
			for i in range(0,self.count-3) :
				nums.append( i   )
				nums.append( i+4 )
			nums = np.array(nums,np.float32)

			glBindBuffer(GL_ARRAY_BUFFER,self.bid)
			glBufferData(GL_ARRAY_BUFFER,self.geom,GL_STATIC_DRAW)
			glBindBuffer(GL_ARRAY_BUFFER,0)

			glBindTexture(GL_TEXTURE_BUFFER,self.btex)
			glTexBuffer(GL_TEXTURE_BUFFER,GL_RGBA32F,self.bid)
			glBindTexture(GL_TEXTURE_BUFFER,0)

			glBindBuffer(GL_ARRAY_BUFFER,self.bid)
			glBufferData(GL_ARRAY_BUFFER,self.geom,GL_STATIC_DRAW)
			glBindBuffer(GL_ARRAY_BUFFER,0)

			glBindTexture(GL_TEXTURE_BUFFER,self.btex)
			glTexBuffer(GL_TEXTURE_BUFFER,GL_RGBA32F,self.bid)
			glBindTexture(GL_TEXTURE_BUFFER,0)

			glUseProgram( self.prog )

			mmv = glGetFloatv(GL_MODELVIEW_MATRIX)
			mp  = glGetFloatv(GL_PROJECTION_MATRIX)

			glUniformMatrix4fv(self.loc_mmv,1,GL_FALSE,mmv)
			glUniformMatrix4fv(self.loc_mp ,1,GL_FALSE,mp )

			color = glGetFloatv(GL_CURRENT_COLOR)
			glUniform4f(self.l_color , *color )

			glUniform2i(self.l_screen , self.w , self.h )

			glBindTexture(GL_TEXTURE_BUFFER,self.btex)

			glEnableVertexAttribArray(0)
			glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0 , nums )
			glDrawArrays(GL_POINTS, 0, len(nums)/2)
			glDisableVertexAttribArray(0)

			glBindTexture(GL_TEXTURE_BUFFER,0)

			glUseProgram( 0 )

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

