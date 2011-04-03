
from look.node import Node

from bezier_c0 import BezierC0 
from bezier_c2 import BezierC2

from geom.bezier import Bezier

class Beziers( Node ) :
	BEZIER_C0 , BEZIER_C2 = range(2)

	def __init__( self ) :
		Node.__init__( self )

		self.curves = True
		self.polygons = False

		self.selected = None

	def new( self , pos , type ) :
		if type == Beziers.BEZIER_C0 :
			self.selected = BezierC0( self.curves , self.polygons )
		elif type == Beziers.BEZIER_C2 :
			self.selected = BezierC2( self.curves , self.polygons )

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
			self.selected.move_current( v )

	def toggle( self , what ) :
		if what == Bezier.CURVE :
			self.curves = not self.curves
		elif what == Bezier.POLYGON :
			self.polygons = not self.polygons

		for b in self :
			b.get_geom().set_visibility( Bezier.CURVE   , self.curves   )
			b.get_geom().set_visibility( Bezier.POLYGON , self.polygons )
			b.get_geom().refresh()

