
import math as m 
import numpy as np
from numpy.linalg import linalg as la

from look.node import Node
from geom.point import Point

class Points( Node ) :
	def __init__( self , geom ) :
		Node.__init__( self , geom )

		self.current = None

	def move_current( self , v ) :
		if self.current :
			self.current.translate( *v )
			self.get_geom().refresh()
			return True
		return False

	def new( self , pos , data = None ) :
		n = Node( Point() )
		n.translate(*pos)
		self.add_child( n )

	def delete( self , pos , dist = .05 ) :
		v , p = self.find_nearest( pos , dist )
		if p != None :
			self.del_child( p )

	def select( self , pos , dist ) :
		v , curr = self.find_nearest( pos , dist )
		if id(curr) == id(self.current) :
			self.current = None
		else :
			self.current = curr

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self , mindist )

	def _find_nearest( self , pos , containter , mindist = .05 ) :
		def dist( a , b ) :
			return m.pow(a[0]-b[0],2) + m.pow(a[1]-b[1],2)

		mc = la.dot( self.currp , self.currmv )

		minv= None
		minp= None
		for mp in containter :
			p = la.dot( mc , np.array((mp[0],mp[1],mp[2],1)) )
			p = p / p[3]
			if minv == None or minv > dist( pos , p ) :
				minp = mp
				minv = dist( pos , p )

		if not mindist or minv <= mindist :
			return ( minv , minp )
		else :
			return ( float('inf') , None )

