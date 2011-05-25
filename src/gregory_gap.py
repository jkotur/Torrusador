
import math as m
import numpy as np

import copy as cp

from look.node import Node
from geom.point import Point
from geom.surface import Surface 
from geom.bezier import Bezier

from surface_c0 import SurfaceC0
from surface_c0 import decasteljau
from surface_gregory import SurfaceGregory

from points import Points

import csurf

from OpenGL.GL import *

def split_bezier( pts , t ) :
	if len(pts) <= 0 :
		return 0

	ptsa = [ pts[ 0] ]
	ptsb = [ pts[-1] ]

	for k in reversed(range(1,len(pts))) :
		for i in xrange(0,k) :
			pts[i] = pts[i]*(1.0-t) + pts[i+1]*t
		ptsa.append( pts[0] )
		ptsb.append( pts[k-1] )
	return ptsa , ptsb

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
		self.base_surfs = 0

		self._fill_gap = None

	def draw( self ) :
		Points.draw( self )
		for s in self.surfs : s.draw()

		if self._subsurfs != None and self._fill_gap != None :
			glDepthFunc(GL_NEVER)
			for i in range(self.base_surfs) :
				glBegin(GL_POINTS)
				for j in range(16) :
					glColor3f(0,(j+1.0)/16.0,0)
					glVertex3f(*self._subsurfs[i][j])
				glEnd()
				glColor3f(1,1,1)
			glDepthFunc(GL_LEQUAL)

	def new( self , pos , which ) :
		if len(self) >= self.gapsize or len(self.pts) > 0 : return

		Points.new( self , pos )

		if len(self) < self.gapsize : return

		corners = []
		for p in self :
			corners.append( np.array(( p[0] , p[1] , p[2] ),np.float32) )
		del self[:]

		self.make_pts( corners )

	def make_pts( self , corners ) :
		for i in range(len(corners)-1) :
			self.make_bezier_pts( corners[i] , corners[i+1] )
		self.make_bezier_pts( corners[-1] , corners[0] )

	def make_bezier_pts( self , a , b ) :
		dx = (b - a)/3.0
		dy = np.empty(3,np.float32)
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
		self.base_surfs = len(self.surfs)
		self._subsurfs = np.zeros( (self.base_surfs,16,3) , np.float32 )


	def move_current( self , v ) :
		if self.current == None :
			return

		self.current += v

		for s in self.surfs :
			s.generate()
			self.fill_gap()

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )

	def set_density( self , dens ) :
		self.dens  = dens
		for s in self.surfs :
			s.set_density(dens)

	def fill_gap( self ) :
		if self._fill_gap != None :
			if len(self.surfs)==self.base_surfs :
				z = [ np.zeros(3,np.float32) ] * 20
				pts = [ cp.deepcopy(z) for i in range(self.base_surfs) ]
				for i in range(self.base_surfs) :
					self.surfs.append( SurfaceGregory( ((1,1),self.dens) , pts = pts[i] ) )

			self._fill_gap( self.surfs , self._subsurfs , self.base_surfs )
			for i in range(self.base_surfs) :
				self.surfs[i].generate()
		else :
			del self.surfs[self.base_surfs:]
	def fill_gap_none( self ) :
		self._fill_gap = None
		self.fill_gap()
	def fill_gap_c0( self ) :
		self._fill_gap = csurf.fill_gap_c0
		self.fill_gap()
	def fill_gap_c1( self ) :
		self._fill_gap = csurf.fill_gap_c1
		self.fill_gap()
	def fill_gap_c2( self ) :
		self._fill_gap = csurf.fill_gap_c2
		self.fill_gap()

