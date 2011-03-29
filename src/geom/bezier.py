
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
	def __init__( self , points ) :
		Dummy.__init__(self)

		self.pts = points

		self.settype( GL_LINE_STRIP )

	def set_points( self , points ) :
		self.pts = points

	def geometry( self ) :
		points = []

		ptsx = [ p[0] for p in self.pts ]
		ptsy = [ p[1] for p in self.pts ]
		ptsz = [ p[2] for p in self.pts ]

		for i in range(0,len(self.pts),3) :
			for t in np.arange(0,1.001,.01) :
				points += [ decasteljau( ptsx[i:i+4] , t ) , decasteljau( ptsy[i:i+4], t ) , decasteljau( ptsz[i:i+4], t) ]

		return points

