
from dummy import *

class Curve( Dummy ) :

	POINTS , POLYGON , CURVE = range(3)
	BEZIER , BSPLINE = range(2)

	def __init__( self ) :
		Dummy.__init__(self)

		self.settype( Dummy.SELF )

		self.draw_points  = True
		self.draw_curve   = True
		self.draw_polygon = False

	def set_visibility( self , what , how ) :
		if what == Curve.POINTS :
			self.draw_points = how
		elif what == Curve.CURVE :
			self.draw_curve = how
		elif what == Curve.POLYGON :
			self.draw_polygon = how

