
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
	def __init__( self , bzpts , bzcur , bzpol , bspts , bscur , bspol ) :
		self.bz = Bezier()
		self.bs = Bspline()

		Points.__init__( self , MultiGeom((self.bz,self.bs)) )

		self.bezier_points = bzpts
		self.bspline_points = bspts

		self.bz.set_visibility( Curve.POINTS  , bzpts )
		self.bz.set_visibility( Curve.CURVE   , bzcur )
		self.bz.set_visibility( Curve.POLYGON , bzpol )
		self.bs.set_visibility( Curve.POINTS  , bspts )
		self.bs.set_visibility( Curve.CURVE   , bscur )
		self.bs.set_visibility( Curve.POLYGON , bspol )

		self.bezier = []
		self.deboor = []

		self.state = None

		self.set_data( (self.bezier,self.deboor) )

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BEZIER :
			self.bz.set_visibility( Curve.POINTS  , pts    )
			self.bz.set_visibility( Curve.CURVE   , curves )
			self.bz.set_visibility( Curve.POLYGON , polys  )
			self.bezier_points = pts
		elif type == Curve.BSPLINE :
			self.bs.set_visibility( Curve.POINTS  , pts    )
			self.bs.set_visibility( Curve.CURVE   , curves )
			self.bs.set_visibility( Curve.POLYGON , polys  )
			self.bspline_points = pts

	def find_index( self , cont , elem ) :
		index = None 
		for i in range( len( cont ) ) :
			if id(elem) == id(cont[i]) :
				index = i
				break
		return index

	def convert2bezier( self ) :
		if self.state == Curve.BSPLINE :
			self.deboor2bezier( self.bezier , self.deboor )
			self.bezier.append( np.array((0,0,0)) )
			self.bezier.append( np.array((0,0,0)) )
			self.repairc2( -3 )
		self.state = Curve.BEZIER

	def convert2bspline( self ) :
		if self.state == Curve.BEZIER :
			if len(self.bezier) > 4 :
				del self.bezier[-2:]
			self.bezier2deboor( self.deboor , self.bezier )
			self.deboor2bezier( self.bezier , self.deboor )
		self.state = Curve.BSPLINE

	def move_current( self , v ) :
		if self.current == None :
			return

		i = self.find_index( self.bezier , self.current )
		if i != None :
			self.convert2bezier()
			if i < 3 or i % 3 == 0 :
				self.current += v
				self.repairc2( i )
			self.bezier2deboor( self.deboor , self.bezier )

		i = self.find_index( self.deboor , self.current )
		if i != None :
			self.convert2bspline()
			self.current += v
			self.deboor2bezier( self.bezier , self.deboor )


	def new( self , pos , which ) :
		if which == Curve.BEZIER :
			self.convert2bezier()

			self.bezier.append( np.array(pos) )

			if len(self.bezier) >= 4 :
				self.bezier.append( np.array((0,0,0)) )
				self.bezier.append( np.array((0,0,0)) )
				self.repairc2( -3 )

			self.bezier2deboor( self.deboor , self.bezier)

		elif which == Curve.BSPLINE :
			self.convert2bspline()

			self.deboor.append( np.array(pos) )

			self.deboor2bezier( self.bezier , self.deboor )

	def delete( self , pos , dist = .05 ) :
		v , p = self.find_nearest( pos , dist )

		i = self.find_index( self.bezier , p )
		if i != None :
			if i < 3 :
				self.convert2bezier()
				del self.bezier[ 4:6 ]
				del self.bezier[ i ]
				self.repairc2( 3 )
				self.bezier2deboor( self.deboor , self.bezier)
			elif i % 3 == 0 :
				self.convert2bezier()
				del self.bezier[ i:i+3 ]
				self.repairc2( i )
				self.bezier2deboor( self.deboor , self.bezier)

		i = self.find_index( self.deboor , p )
		if i != None :
			self.convert2bspline()
			del self.deboor[i]
			self.deboor2bezier( self.bezier , self.deboor )

	def find_nearest( self , pos , mindist = .05 ) :
		v = float('inf')
		p = None
		if self.bezier_points :
			v , p = self._find_nearest( pos , self.bezier , mindist )
		if p != None : return v , p
		if self.bspline_points :
			v , p = self._find_nearest( pos , self.deboor , mindist )
		return v , p


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
			bezier.append( copy(bezier[-1]) )

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
		del bezier[:]
		dlen = len(deboor)
		if dlen < 2 :
			bezier.append( deboor[0] )
			return

		p1 = ( deboor[0] + 2.0*deboor[1] ) / 3.0

		for i in xrange(1,dlen-2) :
			p2 = ( 2*deboor[i] +   deboor[i+1] ) / 3.0
			bezier.append( (p1+p2) / 2.0 )
			bezier.append(p2)

			p1 = (   deboor[i] + 2*deboor[i+1] ) / 3.0
			bezier.append(p1)

		p2 = ( 2*deboor[dlen-2] +   deboor[dlen-1] ) / 3.0
		bezier.append( (p1+p2) / 2.0 )

