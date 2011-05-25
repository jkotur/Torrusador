
import math as m
import numpy as np
from scipy import interpolate
from scipy import optimize
import scipy as sp

import scipy.spatial.distance as dist

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

def center( p0 , pts ) :
	return [ dist.euclidean(p,p0) for p in pts ]

def get_array( tab , i ) :
	return tab[i]

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
		self._subsurfs = None

	def draw( self ) :
		Points.draw( self )
		for s in self.surfs : s.draw()

		if self._subsurfs != None :
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

	def _fill_gap_c0( self ) :
		snum = self.base_surfs

		if len(self.surfs) == self.base_surfs :
			self._subsurfs = np.zeros( (snum,16,3) , np.float32 )
			z = [ np.zeros(3,np.float32) ] * 20
			pts = [ cp.deepcopy(z) for i in range(len(self.surfs)) ]
		else :
			pts = [ s.get_pts() for s in self.surfs[self.base_surfs:] ]

		q = np.empty( (snum,3) , np.float32 )

		for i in range(snum) :
			csurf.split_bezier_surf( self.surfs[i].get_pts() , self._subsurfs[i] )

		for i in range(snum) :
			pts[i][ 1] = get_array( self._subsurfs[i-1] ,  9 )
			pts[i][ 2] = get_array( self._subsurfs[i-1] , 10 )
			pts[i][ 3] = get_array( self._subsurfs[i-1] , 11 )
			pts[i][ 0] = get_array( self._subsurfs[i  ] ,  0 )
			pts[i][ 4] = get_array( self._subsurfs[i  ] ,  1 )
			pts[i][ 8] = get_array( self._subsurfs[i  ] ,  2 )
			pts[i][12] = get_array( self._subsurfs[i  ] ,  3 )

			pts[i][ 6] = 2*pts[i][ 1] - get_array( self._subsurfs[i-1] , 13 )
			pts[i][ 9] = 2*pts[i][ 2] - get_array( self._subsurfs[i-1] , 14 )
			pts[i][ 7] = 2*pts[i][ 3] - get_array( self._subsurfs[i-1] , 15 )

			pts[i][ 5] = 2*pts[i][ 4] - get_array( self._subsurfs[i  ] ,  5 )
			pts[i][17] = 2*pts[i][ 8] - get_array( self._subsurfs[i  ] ,  6 )
			pts[i][13] = 2*pts[i][12] - get_array( self._subsurfs[i  ] ,  7 )

			pts[i][10] = pts[i][ 9]
			pts[i][16] = pts[i][17]

			q[i] = (3.0*pts[i][7]-1.0*pts[i][3])/2.0

		p0 = np.mean(q,0)
		p0 ,  err = optimize.leastsq( center , p0 , q )

		if err > 4 :
			print 'leastsq err' , err
			p0 = np.mean(q,0)

		for i in range(snum) :
			pts[i][15] = p0
			pts[i][11] = (2.0*q[i]+p0)/3.0

		for i in range(snum) :
			pts[i-1][14] = pts[i][11]

		x = [ 0.0 , 1.0 , 3.0 ]
		for i in range(snum) :
			y = np.array(
					( pts[i][ 2]-pts[i][ 3] ,
					  pts[i][10]-pts[i][ 7] ,
					  pts[i][14]-pts[i][15] ) , np.float32 )
			pts[i][18] = pts[i][11] + interpolate.interp1d( x , y , 'quadratic' , 0 , False )(2.0)
			pts[i][18] = np.array( pts[i][18] , np.float32 )
			y = np.array(
					( pts[i][ 8]-pts[i][12] ,
					  pts[i][16]-pts[i][13] ,
					  pts[i][11]-pts[i][15] ) , np.float32 )
			pts[i][19] = pts[i][14] + interpolate.interp1d( x , y , 'quadratic' , 0 , False )(2.0)
			pts[i][19] = np.array( pts[i][19] , np.float32 )

		if len(self.surfs) == self.base_surfs :
			for i in range(snum) :
				self.surfs.append( SurfaceGregory( ((1,1),self.dens) , pts = pts[i] ) )

		return pts

	def _fill_gap_c1( self ) :
		pts = self._fill_gap_c0()

		self.surfs[0                ].get_pts()[4] = 3*pts[0][0]-2*pts[0][1]
		self.surfs[self.base_surfs-1].get_pts()[7] = 3*pts[0][0]-2*pts[0][4]
		for i in range(1,self.base_surfs) :
			self.surfs[i  ].get_pts()[4] = 3*pts[i][0]-2*pts[i][1]
			self.surfs[i-1].get_pts()[7] = 3*pts[i][0]-2*pts[i][4]

		return pts

	def _fill_gap_c2( self ) :
		pts = self._fill_gap_c1()

		for i in range(self.base_surfs) :
			p = self.surfs[i].get_pts()
			p[6] = p[7]+p[2]-p[3]
			p[5] = p[4]+p[1]-p[0]

	def fill_gap( self ) :
		if self._fill_gap != None :
			self._fill_gap()
			for i in range(self.base_surfs) :
				self.surfs[i].generate()
		else :
			del self.surfs[self.base_surfs:]
	def fill_gap_none( self ) :
		self._fill_gap = None
		self.fill_gap()
	def fill_gap_c0( self ) :
		self._fill_gap = self._fill_gap_c0
		self.fill_gap()
	def fill_gap_c1( self ) :
		self._fill_gap = self._fill_gap_c1
		self.fill_gap()
	def fill_gap_c2( self ) :
		self._fill_gap = self._fill_gap_c2
		self.fill_gap()

