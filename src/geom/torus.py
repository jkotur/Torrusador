
from dummy import *

import numpy as np
import math as m

class Torus( Dummy ) :
	
	def __init__( self ) :
		self.R = .5
		self.r = .1
		self.N = 8
		self.n = 32

		Dummy.__init__(self)

		self.settype( GL_LINE_STRIP )

	def geometry( self ) :
		points = []

		for a in np.linspace(0,m.pi*2,self.n,False) :
			for b in np.linspace(0,m.pi*2,self.N+1) :
				points += [ (self.R+self.r*m.cos(a))*m.cos(b) , (self.R+self.r*m.cos(a))*m.sin(b) , self.r*m.sin(a) ]

		for b in np.linspace(0,m.pi*2,self.N,False) :
			for a in np.linspace(0,m.pi*2,self.n+1) :
				points += [ (self.R+self.r*m.cos(a))*m.cos(b) , (self.R+self.r*m.cos(a))*m.sin(b) , self.r*m.sin(a) ]

		return points

