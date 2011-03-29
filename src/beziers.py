
from look.node import Node

from points import Points
from geom.bezier import Bezier

class Beziers( Node ) :
	def __init__( self ) :
		Node.__init__( self )

		self.selected = None

	def new( self , pos ) :
		b = Bezier(None)
		self.selected = Points( b )
		b.set_points( self.selected )

		self.selected.new( pos )
		self.add_child( self.selected )

	def delete( self , pos , dist = .05 ) :
		s = self.find_near( pos , dist )
		if not s[1] :
			return
		if self.selected == s[1] :
			self.selected = None
		self.del_child( s[1] )

	def select( self , pos , dist = .05 ) :
		v , self.selected = self.find_near( pos , dist )

	def find_near( self , pos , dist ) :
		minv = None
		for pts in self :
			v , p = pts.find_nearest( pos , dist )
			if minv == None or minv > v :
				out = pts
				minv = v

		if not minv :
			return float('inf') , None
		else :
			return minv , out

	def point_new( self , pos ) :
		if self.selected :
			self.selected.new( pos )
			self.selected.get_geom().refresh()

	def point_delete( self , pos , dist ) :
		if self.selected :
			self.selected.delete( pos , dist )
			self.selected.get_geom().refresh()

	def point_select( self , pos , dist ) :
		if self.selected :
			self.selected.select( pos , dist )
			self.selected.get_geom().refresh()

	def point_move( self , v ) :
		if self.selected :
			if self.selected.get_curr() :
				self.selected.get_curr().translate( *v )
				self.selected.get_geom().refresh()

