
from dummy import *

import numpy as np
import math as m

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

	def set_visibility( self , what , how ) :
		if what == Bezier.CURVE :
			self.draw_curve = how
		elif what == Bezier.POLYGON :
			self.draw_polygon = how

	def set_points( self , points ) :
		self.pts = points

	def geometry( self ) :
		points = []

		ptsx = [ p[0] for p in self.pts ]
		ptsy = [ p[1] for p in self.pts ]
		ptsz = [ p[2] for p in self.pts ]

		if self.draw_curve :
			for i in range(0,len(self.pts),3) :
				for t in np.arange(0,1.001,.01) :
					points += [ decasteljau( ptsx[i:i+4] , t ) , decasteljau( ptsy[i:i+4], t ) , decasteljau( ptsz[i:i+4], t) ]
		
		if self.draw_polygon :
			for p in reversed(self.pts) :
				points += [ p[0] , p[1] ,p[2] ]

		return points

	def draw_self( self ) :
		''' TODO: draw beziers curves '''
		self.settype(GL_LINE_STRIP)
		self.draw()
		self.settype(Dummy.SELF)

