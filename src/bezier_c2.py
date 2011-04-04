
import numpy as np

from look.node import Node
from geom.point import Point

from points import Points

from geom.bspline import Bspline
from geom.bezier import Bezier
from geom.dummy import Dummy
from geom.curve import Curve

from copy import copy

class MultiGeom( Dummy ) :
	def __init__( self , cont = [] ) :
		Dummy.__init__( self )

		self.geoms = cont

	def set_visibility( self , what , how ) :
		for g in self.geoms :
			g.set_visibility( what , how )

	def gfx_init( self ) :
		for g in self.geoms :
			g.gfx_init()

	def draw( self , data = None ) :
		if hasattr(data,'__iter__') :
			for i in range(len(self.geoms)) :
				self.geoms[i].draw( data[i] )
		else :
			for g in self.geoms :
				g.draw( data )

class BezierC2( Points ) :
	def __init__( self , curve_vis = True , polygon_vis = False ) :
		bz = Bezier()
		bs = Bspline()

		Points.__init__( self , MultiGeom((bz,bs)) )

		bz.set_visibility( Curve.POINTS  , True        )
		bz.set_visibility( Curve.CURVE   , curve_vis   )
		bz.set_visibility( Curve.POLYGON , polygon_vis )
		bs.set_visibility( Curve.POINTS  , True        )
		bs.set_visibility( Curve.CURVE   , curve_vis   )
		bs.set_visibility( Curve.POLYGON , polygon_vis )

		self.bezier = []
		self.deboor = [(0,0,0),(0,.1,0)]

		self.set_data( (self.bezier,self.deboor) )

	def find_index( self , cont , elem ) :
		i = None 
		for i in range( len( cont ) ) :
			if id(elem) == id(cont[i]) :
				index = i
				break
		return i

	def move_current( self , v ) :
		if self.current == None :
			return

		i = self.find_index( self.bezier , self.current )

		if i != None :
			if i < 3 or i % 3 == 0 :
				self.current += v
				self.repairc2( i )

			self.bezier2deboor( self.deboor , self.bezier)

	def new( self , pos ) :
		self.bezier.append( np.array(pos) )

		if len(self.bezier) >= 4 :
			self.bezier.append( np.array((0,0,0)) )
			self.bezier.append( np.array((0,0,0)) )
			self.repairc2( -3 )

		self.bezier2deboor( self.deboor , self.bezier)


	def delete( self , pos , dist = .05 ) :
		v , p = self.find_nearest( pos , dist )

		i = self.find_index( self.bezier , p )

		if i != None :
			if i < 3 :
				del self.bezier[ 4:6 ]
				del self.bezier[ i ]
				self.repairc2( 3 )
				self.bezier2deboor( self.deboor , self.bezier)
			elif i % 3 == 0 :
				del self.bezier[ i:i+3 ]
				self.repairc2( i )
				self.bezier2deboor( self.deboor , self.bezier)


	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.bezier , mindist )

	def repairc2( self , index ) :
		if index < 0 : index = len(self.bezier) + index
		for i in range(max(3,index),len(self.bezier),3) :
			self.bezier[ i+1 ]  = 2 * self.bezier[ i   ] - self.bezier[ i-1 ]
			self.bezier[ i+2 ]  = 2 * self.bezier[ i-1 ] - self.bezier[ i-2 ]
			self.bezier[ i+2 ]  = 2 * self.bezier[ i+1 ] - self.bezier[ i+2 ]

	def bezier2deboor( self , deboor , bezier ) :
		del deboor[:]

		if len(bezier) == 1 :
			add = 3
		else :
			add = 2 - (len(bezier)-2) % 3

		for i in xrange(add) :
			bezier.append( bezier[-1] )

		# add middle points
		for i in xrange(1,len(bezier)-1,3) :
			deboor.append( 2 * bezier[i  ] - bezier[i+1] )

		# add first point
		p = 2 * bezier[0] - bezier[1]
		deboor.insert(0 , 3*p - 2*deboor[0])

		deboor.append( 2 * bezier[-2] - bezier[-3] )
		p = 2 * bezier[-1] - bezier[-2]
		deboor.append( 3*p - 2*deboor[-1])

		for i in xrange(add) :
			bezier.pop()

	def deboor2bezier( self , bezier , deboor ) :
		pass

