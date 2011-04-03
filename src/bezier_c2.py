
import numpy as np

from look.node import Node
from geom.point import Point

from points import Points
from geom.bezier import Bezier

from copy import copy

class BezierC2( Points ) :
	def __init__( self , curve_vis = True , polygon_vis = False ) :
		b = Bezier()

		Points.__init__( self , b )

		b.set_visibility( Bezier.CURVE   , curve_vis   )
		b.set_visibility( Bezier.POLYGON , polygon_vis )

		self.points = []

		self.set_data( self.points )

	def move_current( self , v ) :
		if self.current == None :
			return

		for i in range( len( self.points ) ) :
			if id(self.current) == id(self.points[i]) :
				index = i
				break

		if i < 3 or i % 3 == 0 :
			self.current += v
			self.repairc2( i )

	def new( self , pos ) :
		self.points.append( np.array(pos) )

		if len(self.points) >= 4 :
			self.points.append( np.array((0,0,0)) )
			self.points.append( np.array((0,0,0)) )
			self.repairc2( -3 )

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.points , mindist )

	def repairc2( self , index ) :
		if index < 0 : index = len(self.points) + index
		for i in range(max(3,index),len(self.points),3) :
			self.points[ i+1 ]  = 2 * self.points[ i   ] - self.points[ i-1 ]
			self.points[ i+2 ]  = 2 * self.points[ i-1 ] - self.points[ i-2 ]
			self.points[ i+2 ]  = 2 * self.points[ i+1 ] - self.points[ i+2 ]

