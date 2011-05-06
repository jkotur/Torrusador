
import numpy as np

import math as m

from look.node import Node
from geom.point import Point

from points import Points

from geom.bezier import Bezier
from geom.curve import Curve
from geom.surface import Surface 

from copy import copy

import csurf

def rekN( n , i ,  t ) :
	if n == 0 : return 1 if t >= i and t < i + 1 else 0
	n1 = rekN(n - 1, i, t)
	n2 = rekN(n - 1, i + 1, t)
	return n1 * float(t - i) / float(n) + n2 * float(i + n + 1 - t) / float(n)

class SurfaceC2( Points ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False ) :
		self.dv = np.zeros(3)

		self.size = data[0]
		self.dens = data[1]

		gm = Surface()

		self.pts= []

		Points.__init__( self , gm )

		gm.set_visibility( Bezier.POINTS  , pts_vis     )
		gm.set_visibility( Bezier.CURVE   , False )
		gm.set_visibility( Bezier.POLYGON , False )

		self.calc_size()
		self.allocate()

		self.set_data( (self.pts,self.bezy) )

		self.base = []
		for t in np.linspace(3,4,256/4) :
			for j in range(4) :
				self.base.append( rekN( 3 , j , t ) )
		self.base = np.array( self.base , np.float32 )

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BSPLINE :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys )

	def calc_size( self ) :
		self.sized = (self.size[0]*self.dens[0]*3+1 , self.size[1]*self.dens[1]*3+1 )
		self.get_geom().gen_ind(self.sized[0],self.sized[1])

	def allocate( self ) :
		self.bezx = np.zeros(3*self.sized[0]*self.sized[1] , np.float32 )
		self.bezy = np.zeros(3*self.sized[0]*self.sized[1] , np.float32 )

	def set_density( self , dens ) :
		self.dens = dens 
		self.calc_size()
		self.allocate()
		self.set_data( (self.pts,self.bezy) )
		self.bezx , self.bezy = csurf.gen_deboor( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] , self.base )

	def new( self , pos , which ) :
		if len(self) >= 3 or len(self.pts) > 0 : return

		Points.new( self , pos )

		if len(self) < 3 : return

		corners = []
		for p in self :
			corners.append( np.array(( p[0] , p[1] , p[2] )) )
		del self[:]

		corners.append( corners[2] + corners[0] - corners[1] )

		dx = (corners[1] - corners[0]) / (self.size[0]*3)
		dy = (corners[3] - corners[0]) / (self.size[1]*3)

		del self.pts[:]

		for y in range(self.size[1]*3+1) :
			for x in range(self.size[0]*3+1):
				pt = corners[0] + dx * x + dy * y
				self.pts.append( pt )

		self.bezx , self.bezy = csurf.gen_deboor( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] , self.base )

		self.get_geom().set_visibility( Bezier.CURVE , True )

	def move_current( self , v ) :
		if self.current == None :
			return

		self.dv += v

		if np.linalg.norm(self.dv) < .05 :
			return

		self.current += self.dv

		self.dv = np.zeros(3)

		self.bezx , self.bezy = csurf.gen_deboor( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] , self.base )

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )

