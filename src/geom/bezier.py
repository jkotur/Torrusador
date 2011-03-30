
from dummy import *

import numpy as np
import math as m

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
						points += [ decasteljau( self.ptsx[i:i+4] , t ) , decasteljau( self.ptsy[i:i+4], t ) , decasteljau( self.ptsz[i:i+4], t) ]
		
		if self.draw_polygon :
			for p in reversed(self.pts) :
				points += [ p[0] , p[1] ,p[2] ]

		return points

	def draw_self( self ) :
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

