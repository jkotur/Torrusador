
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

def decasteljau( t , pts , knots ) :
		if len(pts) <= 0 :
			return 0

		l = 0       
		while l+1 < len(knots) and knots[l+1] < t : l+= 1
		l+= 1

		n = len(pts) - 1

		def alpha( t , k , i ) :
			return (t-knots[i])/(knots[i+n+1-k]-knots[i])

		print 'nl: ' , t , n , l 

		for k in range(1,n+1) :
			for i in xrange(l-n+k,l+1) :
				pts[i] = pts[i-1]*(1.0-alpha(t,k,i)) + pts[i]*alpha(t,k,i)
				print i , k , pts
		return pts[-1]


class Bspline( Curve ) :

	def __init__( self ) :
		Curve.__init__( self ) 

		self.prog = None

	def get_loc( self , prog , loc ) :
		location = glGetUniformLocation(prog,loc)
		if location in (None,-1): raise ValueError ('No uniform: ' + loc)
		return location                 

	def gfx_init( self ) :
		if self.is_inited : return

		try:
			self.prog = sh.compile_program("shad/bspline")
		except ValueError as ve:
			print "Shader compilation failed: " + str(ve)
			sys.exit(0)

		self.loc_mmv = self.get_loc(self.prog,'modelview' )
		self.loc_mp  = self.get_loc(self.prog,'projection')
		pointsid     = self.get_loc(self.prog,'points'    )

		self.bid  = glGenBuffers(1)
		self.btex = glGenTextures(1)

		glUseProgram( self.prog )
		glUniform1i( pointsid , 0 );
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

		if self.draw_curve :
#            ptsx = [ p[0] for p in data ]
#            ptsy = [ p[1] for p in data ]
#            ptsz = [ p[2] for p in data ]

#            knots = [ 0 , 1 , 2 , 3 , 4 , 5 ]
#            pts = []
#            for i in range(0,self.count-3) :
#                for t in np.linspace(2.0,3.0,32) :
#                    print ptsx[i:i+4]
#                    print ptsy[i:i+4]
#                    print ptsz[i:i+4]
#                    pts += [ 
#                            decasteljau( t , ptsx[i:i+4] , knots ) ,
#                            decasteljau( t , ptsy[i:i+4] , knots ) ,
#                            decasteljau( t , ptsz[i:i+4] , knots ) ,
#                            1.0 ]

#            pts = np.array(pts,np.float32)

#            print pts

#            glColor3f(1,0,0)
#            glEnableClientState(GL_VERTEX_ARRAY)
#            glVertexPointer( 4, GL_FLOAT , 0 , pts )
#            glDrawArrays(GL_POINTS, 0, int(len(pts)/4) )
#            glDisableClientState(GL_VERTEX_ARRAY)

#        if 0 :
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

