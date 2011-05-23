

from OpenGL.GL import *

from surface_c0 import SurfaceC0
import csurf

class SurfaceGregory( SurfaceC0 ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False , pts = None ) :
		SurfaceC0.__init__(self,data,pts_vis,curve_vis,polygon_vis,pts)

	def draw( self ) :
		SurfaceC0.draw( self )

		glPushAttrib(GL_ALL_ATTRIB_BITS)
		glBegin(GL_LINES)
		glColor3f(1,0,0)
		glVertex3f(*self.pts[ 1])
		glVertex3f(*self.pts[ 6])
		glVertex3f(*self.pts[ 4])
		glVertex3f(*self.pts[ 5])
		glVertex3f(*self.pts[ 2])
		glVertex3f(*self.pts[ 9])
		glVertex3f(*self.pts[ 7])
		glVertex3f(*self.pts[10])
		glVertex3f(*self.pts[ 8])
		glVertex3f(*self.pts[17])
		glVertex3f(*self.pts[11])
		glVertex3f(*self.pts[18])
		glVertex3f(*self.pts[13])
		glVertex3f(*self.pts[16])
		glVertex3f(*self.pts[14])
		glVertex3f(*self.pts[19])
		glVertex3f(*self.pts[ 3])
		glVertex3f(*self.pts[ 7])
		glVertex3f(*self.pts[12])
		glVertex3f(*self.pts[13])
		glVertex3f(*self.pts[13])
		glVertex3f(*self.pts[16])
		glVertex3f(*self.pts[ 7])
		glVertex3f(*self.pts[10])
		glEnd()
		glPopAttrib()

	def new( self , pos , which ) :
		raise NotImplementedError("cannot construct Gregory's surface")

	def generate( self ) :
		self.bezx , self.bezy = csurf.gen_gregory( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] )

