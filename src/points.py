
import math as m 

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

	def new( self , pos ) :
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
			return m.pow(a[0]-b[0],2) + m.pow(a[1]-b[1],2) + m.pow(a[2]-b[2],2)

		minv= None
		minp= None
		for p in containter :
			if minv == None or minv > dist( pos , (p[0],p[1],p[2]) ) :
				minp = p
				minv = dist( pos , (p[0],p[1],p[2]) )

		if not mindist or minv <= mindist :
			return ( minv , minp )
		else :
			return ( float('inf') , None )

