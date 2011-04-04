
from dummy import *

class Curve( Dummy ) :

	POINTS , POLYGON , CURVE = range(3)

	def __init__( self ) :
		Dummy.__init__(self)

		self.settype( Dummy.SELF )

		self.draw_curve   = True
		self.draw_polygon = False
		self.draw_points  = True

	def set_visibility( self , what , how ) :
		if what == Curve.POINTS :
			self.draw_polygon = how
		elif what == Curve.CURVE :
			self.draw_curve = how
		elif what == Curve.POLYGON :
			self.draw_polygon = how

