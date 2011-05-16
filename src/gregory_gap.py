
import numpy as np

import math as m

from look.node import Node
from geom.point import Point
from geom.surface import Surface 
from geom.bezier import Bezier

from surface_c0 import SurfaceC0

from points import Points

import csurf

class GregoryGap( Points ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False ) :
		self.dens = data[1]
		self.gapsize = max(data[0][0],3)

		gm = Surface()
		Points.__init__( self , gm )

		gm.set_visibility( Bezier.POINTS  , pts_vis     )
		gm.set_visibility( Bezier.CURVE   , False )
		gm.set_visibility( Bezier.POLYGON , False )

		self.pts     = []
		self.surfs   = []
		self.corners = []

		self.set_data( (self,None) )

	def draw( self ) :
		Points.draw( self )
		for s in self.surfs : s.draw()

	def new( self , pos , which ) :
		if len(self) >= self.gapsize or len(self.pts) > 0 : return

		Points.new( self , pos )

		if len(self) < self.gapsize : return

		corners = []
		for p in self :
			corners.append( np.array(( p[0] , p[1] , p[2] )) )
		del self[:]

		self.make_pts( corners )

	def make_pts( self , corners ) :
		for i in range(len(corners)-1) :
			self.make_bezier_pts( corners[i] , corners[i+1] )
		self.make_bezier_pts( corners[-1] , corners[0] )

	def make_bezier_pts( self , a , b ) :
		dx = (b - a)/3.0
		dy = np.empty(3)
		dy[0] =-dx[1]
		dy[1] = dx[0]
		dy[2] = dx[2]
		beg = len(self.pts)
		for y in range(4) :
			for x in range(4) :
				if y == 0 and x == 0 :
					pt = a
				elif y == 0 and x == 3 :
					pt = b
				else :
					pt = a + dx * x + dy * y
				self.pts.append( pt )
		self.surfs.append( SurfaceC0( ((1,1),self.dens) , pts = self.pts[beg:beg+16] ) )

	def move_current( self , v ) :
		if self.current == None :
			return

		self.current += v

		for s in self.surfs :
			s.generate()

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )

	def set_density( self , dens ) :
		for s in self.surfs :
			s.set_density(dens)

