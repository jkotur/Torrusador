
from points import Points
from geom.bezier import Bezier

class BezierC0( Points ) :
	def __init__( self , curve_vis = True , polygon_vis = False ) :
		b = Bezier()

		Points.__init__( self , b )

		b.set_visibility( Bezier.CURVE   , curve_vis   )
		b.set_visibility( Bezier.POLYGON , polygon_vis )

		self.set_data( self )

