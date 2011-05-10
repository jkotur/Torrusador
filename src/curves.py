
from look.node import Node

from bezier_c0 import BezierC0 
from bezier_c2 import BezierC2
from interpolation import Interpolation
from surface_c0 import SurfaceC0
from surface_c2 import SurfaceC2
from pipe import Pipe

from geom.bezier import Bezier
from geom.curve import Curve

class Curves( Node ) :
	BEZIER_C0 , BEZIER_C2 , INTERPOLATION , SURFACE_C0 , SURFACE_C2 , SURFACE_PIPE = range(6)

	def __init__( self ) :
		Node.__init__( self )

		self.bz_points   = True
		self.bz_curves   = True
		self.bz_polygons = False

		self.bs_points   = True
		self.bs_curves   = False
		self.bs_polygons = False

		self.selected = None

		self.w = 0
		self.h = 0

	def set_screen_size( self , w , h ) :
		self.w = w
		self.h = h
		for b in self :
			b.set_screen_size( w , h )

	def new( self , pos , which_cur , pre_data = None , post_data = None ) :
		if which_cur == Curves.BEZIER_C0 :
			self.selected = BezierC0( self.bz_points , self.bz_curves , self.bz_polygons )
		elif which_cur == Curves.BEZIER_C2 :
			self.selected = BezierC2(
								self.bz_points , self.bz_curves , self.bz_polygons ,
								self.bs_points , self.bs_curves , self.bs_polygons )
		elif which_cur == Curves.INTERPOLATION :
			self.selected = Interpolation( )
		elif which_cur == Curves.SURFACE_C0 :
			self.selected = SurfaceC0( pre_data , self.bz_points , self.bz_curves , self.bz_polygons )
		elif which_cur == Curves.SURFACE_C2 :
			self.selected = SurfaceC2( pre_data , self.bz_points , self.bz_curves , self.bz_polygons )
		elif which_cur == Curves.SURFACE_PIPE :
			self.selected = Pipe( pre_data , self.bz_points , self.bz_curves , self.bz_polygons )

		self.selected.new( pos , post_data )
		self.add_child( self.selected )

		self.selected.set_screen_size( self.w , self.h )

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

	def point_new( self , which , pos ) :
		if self.selected :
			self.selected.new( pos , which )
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

	def toggle( self , which , what ) :
		if which == Curve.BEZIER :
			if what == Curve.POINTS :
				self.bz_points = not self.bz_points
			elif what == Bezier.CURVE :
				self.bz_curves = not self.bz_curves
			elif what == Bezier.POLYGON :
				self.bz_polygons = not self.bz_polygons
		elif which == Curve.BSPLINE :
			if what == Curve.POINTS :
				self.bs_points = not self.bs_points
			elif what == Bezier.CURVE :
				self.bs_curves = not self.bs_curves
			elif what == Bezier.POLYGON :
				self.bs_polygons = not self.bs_polygons

		for b in self :
			b.set_visibility( Curve.BEZIER , self.bz_points , self.bz_curves , self.bz_polygons )
			b.set_visibility( Curve.BSPLINE, self.bs_points , self.bs_curves , self.bs_polygons )
			b.get_geom().refresh()

	def set_surf_density( self , dens ) :
		for b in self :
			if isinstance(b,SurfaceC0) or isinstance(b,SurfaceC2) :
				b.set_density( dens )

