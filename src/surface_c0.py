
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

def decasteljau( pts , t ) :
        if len(pts) <= 0 :
                return 0

        for k in reversed(range(0,len(pts))) :
                for i in xrange(0,k) :
                        pts[i] = pts[i]*(1.0-t) + pts[i+1]*t
        return pts[0]

class SurfaceC0( Points ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False , pts = None ) :
		self.dv = np.zeros(3)

		self.size = data[0]
		self.dens = data[1]

		gm = Surface()

		self.pts = [] if pts == None else pts

		Points.__init__( self , gm )

		gm.set_visibility( Bezier.POINTS  , pts_vis     )
		gm.set_visibility( Bezier.CURVE   , False )
		gm.set_visibility( Bezier.POLYGON , False )

		self.calc_size()
		self.allocate()

		self.set_data( (self.pts,self.bezy) )

		if self.pts != [] :
			self.generate()
			self.get_geom().set_visibility( Bezier.CURVE , True )

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BEZIER :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys )

	def calc_size( self ) :
		self.sized = (self.size[0]*self.dens[0]*3+1 , self.size[1]*self.dens[1]*3+1 )
		self.get_geom().gen_ind(self.sized[0],self.sized[1])

	def allocate( self ) :
		self.bezx = np.zeros( 3*self.sized[0]*self.sized[1] , np.float32 )
		self.bezy = np.zeros( 3*self.sized[0]*self.sized[1] , np.float32 )

	def set_density( self , dens ) :
		self.dens = dens 
		self.calc_size()
		self.allocate()
		self.set_data( (self.pts,self.bezy) )
		self.generate()

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

		self.generate()

		self.get_geom().set_visibility( Bezier.CURVE , True )

	def generate( self ) :
		self.bezx , self.bezy = csurf.gen_bezier( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] )
	

	def generate_python( self , pts , bezx , bezy , zx , zy , sx , sy , dx , dy ) :
		py = 0
		for y in range(0,self.sized[1],dy) :
			px = 0
			for x in range(0,self.sized[0]-1,dx*3):
				id = px+py*(self.size[0]*3+1)
				tmp = pts[id:id+4]
				id = x+y*sx
				j = 0
				for t in np.linspace(0,1,dx*3+1) :
					bezx[id+j] = decasteljau( copy(tmp) , t )
					j+=1
				px += 3
			py += 1

		tmp = [0]*4
		for x in range(self.sized[0]) :
			for y in range(0,self.sized[1]-1,dy*3) :
				id = y+x*sy
				for i in range(4) :
					tmp[i] = bezx[x+(y/dy+i)*dy*sx]
				j = 0 
				for t in np.linspace(0,1,dy*3+1) :
					bezy[id+j] = decasteljau( copy(tmp) , t )
					j+=1

		return bezx , bezy

	def move_current( self , v ) :
		if self.current == None :
			return

		self.dv += v

		self.current += self.dv

		self.dv = np.zeros(3)

		self.generate()

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )

