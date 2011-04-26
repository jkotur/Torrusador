
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

class Bezier( Curve ) :

	def __init__( self , breakpoint = 0 ) :
		Curve.__init__(self)

		self.breakpoint = breakpoint*3 + 1 if breakpoint != 0 else 0

		self.prog = None

	def draw_self( self , data ) :
		self.draw_shad(data)

	def get_loc( self , prog , loc ) :
		location = glGetUniformLocation(prog,loc)
		if location in (None,-1): raise ValueError ('No uniform: ' + loc)
		return location                 

	def gfx_init( self ) :
		if self.is_inited : return

		try:
			self.prog = sh.compile_program("shad/bez_bres")
		except ValueError as ve:
			print "Shader compilation failed: " + str(ve)
			sys.exit(0)

		self.loc_mmv = self.get_loc(self.prog,'modelview' )
		self.loc_mp  = self.get_loc(self.prog,'projection')
		pointsid     = self.get_loc(self.prog,'points'    )
		self.l_color = self.get_loc(self.prog,'color'     )
		self.l_screen= self.get_loc(self.prog,'screen'    )

		self.bid  = glGenBuffers(1)
		self.btex = glGenTextures(1)

		glUseProgram( self.prog )
		glUniform1i( pointsid , 0 );
		glUseProgram( 0 )

		self.is_inited = True

	def draw_shad( self , data ) :
		if len(data) == 0 : return

		self.geom = []
		for p in data :
			self.geom.append(p[0])
			self.geom.append(p[1])
			self.geom.append(p[2])
			self.geom.append(1)
		self.geom = np.array(self.geom,np.float32)
		self.count = len(self.geom)/4

		if self.draw_curve :
			nums = [0]
			i = 3
			while i<self.count :
				nums.append( i+1 )
				if self.breakpoint != 0 and (i+1)%self.breakpoint == 0 : i+=1
				nums.append( i )
				i += 3
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

