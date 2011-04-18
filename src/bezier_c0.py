
from points import Points
from geom.bezier import Bezier
from geom.curve import Curve

class BezierC0( Points ) :
	def __init__( self , pts_vis = True , curve_vis = True , polygon_vis = False ) :
		b = Bezier()

		Points.__init__( self , b )

		b.set_visibility( Bezier.POINTS  , pts_vis     )
		b.set_visibility( Bezier.CURVE   , curve_vis   )
		b.set_visibility( Bezier.POLYGON , polygon_vis )

		self.set_data( self )

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BEZIER :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys  )

