
import math as m 

from look.node import Node
from geom.point import Point

class Points( Node ) :
	def __init__( self , geom ) :
		Node.__init__( self , geom )

		self.current = None

	def get_curr( self ) :
		return self.current

	def new( self , pos ) :
		n = Node( Point() )
		n.translate(*pos)
		self.add_child( n )

	def delete( self , pos , dist = .05 ) :
		v , p = self.find_nearest( pos , dist )
		if p :
			self.del_child( p )

	def select( self , pos , dist ) :
		v , curr = self.find_nearest( pos , dist )
		if curr == self.current :
			self.current = None
		else :
			self.current = curr

	def find_nearest( self , pos , mindist = .05 ) :
		def dist( a , b ) :
			return m.pow(a[0]-b[0],2) + m.pow(a[1]-b[1],2) + m.pow(a[2]-b[2],2)

		minv= None
		minp= None
		for p in self :
			if minv == None or minv > dist( pos , p.get_pos() ) :
				minp = p
				minv = dist( pos , p.get_pos() )

		if not mindist or minv <= mindist :
			return ( minv , minp )
		else :
			return ( float('inf') , None )

