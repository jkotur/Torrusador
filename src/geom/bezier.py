
from dummy import *

import ctypes

import sys

import numpy as np
import math as m

from OpenGL.GL import *
from OpenGL.GL.ARB import *
from OpenGL.GL.EXT import *

import shaders as sh

from numpy.linalg import linalg as la

def decasteljau( pts , t ) :
	if len(pts) <= 0 :
		return 0

	for k in reversed(range(0,len(pts))) :
		for i in xrange(0,k) :
			pts[i] = pts[i]*(1.0-t) + pts[i+1]*t
	return pts[0]

class Bezier( Dummy ) :

	POINTS , POLYGON , CURVE = range(3)

	def __init__( self , points ) :
		Dummy.__init__(self)

		self.pts = points

		self.settype( Dummy.SELF )

		self.draw_curve = True
		self.draw_polygon = False

		self.moved = None

		self.prog = None

	def refresh( self , p = None ) :
		Dummy.refresh( self )
#        self.moved = p

	def set_visibility( self , what , how ) :
		if what == Bezier.CURVE :
			self.draw_curve = how
		elif what == Bezier.POLYGON :
			self.draw_polygon = how

	def set_points( self , points ) :
		self.pts = points

	def geometry( self ) :
		points = []

		if self.draw_curve :
			for i in range(0,len(self.pts),3) :
#                if self.moved not in self.pts[i:i+4] :
#                    continue
#                else :
#                    self.moved = None
				if self.dists[i/3] > -.1 :
					for t in np.linspace(0,1,500.0/max(self.dists[i/3],1),True) :
						points += [ decasteljau( self.ptsx[i:i+4] , t ) , decasteljau( self.ptsy[i:i+4], t ) , decasteljau( self.ptsz[i:i+4], t) , 1 ]
		
		if self.draw_polygon :
			for p in reversed(self.pts) :
				points += [ p[0] , p[1] ,p[2] , 1 ]

		return points

	def draw_self( self , data ) :
		self.draw_shad(data)

	def get_loc( self , prog , loc ) :
		location = glGetUniformLocation(prog,loc)
		if location in (None,-1): raise ValueError ('No uniform: ' + loc)
		return location                 

	def gfx_init( self ) :
		if self.is_inited : return

		try:
			self.prog = sh.compile_program("shad/bez_bres",GL_POINTS,GL_LINE_STRIP)
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

	def draw_shad( self , data ) :
		self.geom = []
		for p in self.pts :
			self.geom.append(p[0])
			self.geom.append(p[1])
			self.geom.append(p[2])
			self.geom.append(1)
		self.geom = np.array(self.geom,np.float32)
		self.count = len(self.geom)/4

		nums = [0]
		for i in range(3,self.count,3) :
			nums.append( i+1 )
			nums.append( i )
		nums.append(self.count)
		nums = np.array(nums,np.float32)

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

	def draw_old( self , data ) :
		''' TODO: draw beziers curves in magic way '''
		self.ptsx = [ p[0] for p in self.pts ]
		self.ptsy = [ p[1] for p in self.pts ]
		self.ptsz = [ p[2] for p in self.pts ]
		self.dists = [ 0 for i in range(0,len(self.pts)) ]

		m = glGetFloatv(GL_TRANSPOSE_MODELVIEW_MATRIX)
		e = la.dot( la.inv(np.reshape(m,(4,4))) , (0,0,0,1) )

		def norm2( v ) :
			return - v[0] - v[1] - v[2]
		def dist( vs ) :
			return sum([ norm2((p[0]-e[0],p[1]-e[1],p[2]-e[2])) for p in vs])/float(len(vs))

		for i in range(0,len(self.pts),3) :
			self.dists[i/3] = dist( self.pts[i:i+4] )

		self.refresh()

		self.settype(GL_LINE_STRIP)
		self.draw()
		self.settype(Dummy.SELF)

