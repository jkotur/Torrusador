
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

class Bezier( Dummy ) :

	POINTS , POLYGON , CURVE = range(3)

	def __init__( self ) :
		Dummy.__init__(self)

		self.settype( Dummy.SELF )

		self.draw_curve   = True
		self.draw_polygon = False
		self.draw_points  = True

		self.prog = None

	def refresh( self , p = None ) :
		Dummy.refresh( self )

	def set_visibility( self , what , how ) :
		if what == Bezier.CURVE :
			self.draw_curve = how
		elif what == Bezier.POLYGON :
			self.draw_polygon = how

	def geometry( self ) :
		return []

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
		for p in data :
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

		if self.draw_curve :
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

