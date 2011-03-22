
import math as m 

from look.node import Node
from geom.point import Point

class Points( Node ) :
	def __init__( self ) :
		Node.__init__( self )

		self.current = None

	def get_curr( self ) :
		return self.current

	def new( self , pos ) :
		n = Node( Point() )
		n.translate(*pos)
		self.add_child( n )

	def delete( self , pos ) :
		n = self.find_nearest( pos )
		if n :
			self.del_child( n )

	def select( self , pos ) :
#        if self.current :
#            self.current.set_color( (1,1,1) )

		curr = self.find_nearest( pos )
		if curr == self.current :
			self.current = None
		else :
			self.current = curr 

#        if self.current :
#            self.current.set_color( (1,.45,0) )

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
			return minp
		else :
			return None

