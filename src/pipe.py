
from copy import copy

import math as m 
import numpy as np
import numpy.linalg as la

from surface_c2 import SurfaceC2 

import transformations as tr

import csurf

class Pipe( SurfaceC2 ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False , pts = [] ) :
		data = ( (max(data[0][0],3),data[0][1]) , data[1] )

		if pts != [] :
			u = data[0][0]
			for v in reversed(range(data[0][1]+3)) :
				pts.insert( u*(v+1) , pts[u*v+2] )
				pts.insert( u*(v+1) , pts[u*v+1] )
				pts.insert( u*(v+1) , pts[u*v  ] )

		SurfaceC2.__init__(self,data,pts_vis,curve_vis,polygon_vis,pts)

	def iter_pts( self ) :
		for v in range(self.size[1] + 3) :
			for u in range(self.size[0]) :
				yield self.pts[u+v*(self.size[0]+3)]

	def make_pts( self , corners ) :
		dx = (corners[3] - corners[0])
		dx = dx / la.norm(dx)
		dy = (corners[1] - corners[0]) / (self.size[1]+3-1)
		dz = np.cross( dx , dy )
		dz = dz / la.norm(dz)
		ax = np.cross( dx , dz )
		ax = ax / la.norm(ax)

		an = 2.0 * m.pi / float(self.size[0]) 
		rot = tr.rotation_matrix( an , ax )

		ox = (corners[3] + corners[0]) / 2.0
		rx = np.resize( ox - corners[0] , 4 )

		del self.pts[:]

		for y in range(self.size[1]+3) :
			drx = copy(rx)
			for x in range(self.size[0]) :
				pt = ox + np.resize(drx,3) 
				self.pts.append(     pt )
				drx = np.dot( drx , rot )
			self.pts.append( self.pts[-self.size[0]] )
			self.pts.append( self.pts[-self.size[0]] )
			self.pts.append( self.pts[-self.size[0]] )
			ox += dy 

