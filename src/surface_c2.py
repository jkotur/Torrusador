
import numpy as np
import numpy.linalg as la

import math as m

from look.node import Node
from geom.point import Point

from points import Points

from geom.bezier import Bezier
from geom.curve import Curve
from geom.surface import SurfaceTrimmed

from trimming import *

from copy import copy

import csurf

from OpenGL.GL import *

def rekN( n , i ,  t ) :
	if n == 0 : return 1 if t >= i and t < i + 1 else 0
	n1 = rekN(n - 1, i, t)
	n2 = rekN(n - 1, i + 1, t)
	return n1 * float(t - i) / float(n) + n2 * float(i + n + 1 - t) / float(n)

class SurfaceC2( Points ) :
	def __init__( self , data , pts_vis = True , curve_vis = True , polygon_vis = False , pts = None ) :
		self.dv = np.zeros(3)

		self.size = data[0]
		self.dens = data[1]

		gm = SurfaceTrimmed()

		self.pts = pts if pts != None else []

		Points.__init__( self , gm )

		gm.set_visibility( Bezier.POINTS  , pts_vis     )
		gm.set_visibility( Bezier.CURVE   , False )
		gm.set_visibility( Bezier.POLYGON , False )

		# trimming data
		self.trimm_curr = None
		self.reset_trimms() 

		self.calc_size()
		self.gen_ind()
		self.allocate()

		self.set_data( (self.pts,self.bezy) )

		i=0
		self.base = []
		for t in np.linspace(3,4,256/4+1) :
			for j in range(4) :
				i+=1
				self.base.append( rekN( 3 , j , t ) )
		self.base = np.array( self.base , np.float32 )

		if self.pts != [] :
			self.generate()
			self.get_geom().set_visibility( Bezier.CURVE , True )

		# debug data
		self.trim_p0 = None
		self.trimming_curve = None

	def draw( self ) :
		Points.draw( self )

		self.draw_debug_trim_curve()

	def draw_debug_trim_curve( self ) :
		if self.trim_p0 != None :
			glColor3f(1,0,0)
			glBegin(GL_POINTS)
			glVertex3f( *self.trim_p0 )
			glEnd()
			glColor3f(1,1,1)

		if self.trimming_curve != None :
			glColor3f(1,0,0)
			glBegin(GL_LINE_STRIP)
			for p in self.trimming_curve :
				glVertex3f(*p)
			glEnd()
			glColor3f(1,1,1)

	def draw_debug_derivatives( self ) :
		v = 11.5
		glColor3f(1,0,0)
		glBegin(GL_LINES)
		p = csurf.bspline_surf        ( 0 , v , self.array_pts )
		dv= csurf.bspline_surf_prime_v( 0 , v , self.array_pts )
		du= csurf.bspline_surf_prime_u( 0 , v , self.array_pts )
		glVertex3f( p[0] , p[1] , p[2] )
		glVertex3f(*(p+dv) )
		glVertex3f( p[0] , p[1] , p[2] )
		glVertex3f(*(p+du) )
		glVertex3f( p[0] , p[1] , p[2] )
		for i in np.linspace(float(self.size[0])/64,self.size[0],64,False) :
			p = csurf.bspline_surf        ( i , v , self.array_pts )
			dv= csurf.bspline_surf_prime_v( i , v , self.array_pts )
			du= csurf.bspline_surf_prime_u( i , v , self.array_pts )
			glVertex3f( p[0] , p[1] , p[2] )
			glVertex3f( p[0] , p[1] , p[2] )
			glVertex3f(*(p+dv) )
			glVertex3f( p[0] , p[1] , p[2] )
			glVertex3f(*(p+du) )
			glVertex3f( p[0] , p[1] , p[2] )
		p = csurf.bspline_surf        ( self.size[0] , v , self.array_pts )
		dv= csurf.bspline_surf_prime_v( self.size[0] , v , self.array_pts )
		du= csurf.bspline_surf_prime_u( self.size[0] , v , self.array_pts )
		glVertex3f( p[0] , p[1] , p[2] )
		glVertex3f(*(p+dv) )
		glVertex3f( p[0] , p[1] , p[2] )
		glVertex3f(*(p+du) )
		glVertex3f( p[0] , p[1] , p[2] )
		glEnd()
		glColor3f(1,1,1,0)

	def get_uv( self ) :
		return self.size
	
	def get_pts( self ) :
		return self.pts

	def get_array_pts( self ) :
		for y in range(self.size[1]+3) :
			for x in range(self.size[0]+3):
				self.array_pts[x,y] = np.array( self.pts[ x + y*(self.size[0]+3) ] , np.double )
		return self.array_pts 

	def iter_pts( self ) :
		for p in self.pts :
			yield p

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BSPLINE :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys )

	def set_select( self , k ) :
		self.get_geom().set_select( k )

	def calc_size( self ) :
		self.sized = (self.size[0]*self.dens[0]*3+1 , self.size[1]*self.dens[1]*3+1 )

	def gen_ind( self ) :
		return self.get_geom().gen_ind(self.sized[0],self.sized[1],self.size[0],self.size[1],self.trimms)

	def allocate( self ) :
		self.bezx = np.zeros(3*self.sized[0]*self.sized[1] , np.float32 )
		self.bezy = np.zeros(3*self.sized[0]*self.sized[1] , np.float32 )

		self.array_pts = np.empty( (self.size[0]+3,self.size[1]+3,3) , np.double )

	def add_u_min( self , u ) :
		if self.trimm_curr != None :
			self.trimm_curr.set_u_min( u )

	def add_v_min( self , v ) :
		if self.trimm_curr != None :
			self.trimm_curr.set_v_min( v )

	def add_u_max( self , u ) :
		if self.trimm_curr != None :
			self.trimm_curr.set_u_max( u )

	def add_v_max( self , v ) :
		if self.trimm_curr != None :
			self.trimm_curr.set_v_max( v )

	def set_loop( self ) :
		if self.trimm_curr != None :
			self.trimm_curr.loop = True

	def reset_trimms( self ) :
		self.trimms = [
				TrimmingBorder( -.2 , -.2 , *self.size ) ,
				TrimmingBorder( self.size[0]+.2 ,self.size[1]+.2 , *self.size ) ]
		self.trimms[-1].offset += .1
		self.fake_trimms = []

	def begin_trimming_curve( self , delta ) :
		self.trimm_curr = TrimmingCurve()
		self.trimm_curr.start( delta )

	def append_trimming_uv( self , u , v ) :
		if self.trimm_curr != None :
			self.trimm_curr.add_back( u , v ) 

	def prepend_trimming_uv( self , u , v ) :
		if self.trimm_curr != None :
			self.trimm_curr.add_front( u , v ) 

	def end_trimming( self , loop = False ) :
		if self.trimm_curr == None :
			return 0
		self.trimm_curr.end( loop )
		if self.trimm_curr.fake :
			print 'Inserting fake trimm' , self.trimm_curr
			self.fake_trimms.insert( -1 , self.trimm_curr )
		else :
			print 'Inserting real trimm' , self.trimm_curr
			self.trimms.insert( -1 , self.trimm_curr )
		self.trimm_curr = None
		return self.gen_ind()

	def generate( self ) :
		self.bezx , self.bezy = csurf.gen_deboor( self.pts , self.bezx , self.bezy , self.size[0] , self.size[1] , self.sized[0] , self.sized[1] , self.dens[0] , self.dens[1] , self.base )
		self.get_array_pts()

	def make_pts( self , corners ) :
		dx = (corners[1] - corners[0]) / (self.size[0]+3-1)
		dy = (corners[3] - corners[0]) / (self.size[1]+3-1)

		del self.pts[:]

		for y in range(self.size[1]+3) :
			for x in range(self.size[0]+3):
				pt = corners[0] + dx * x + dy * y
				self.pts.append( pt )

	def set_density( self , dens ) :
		self.dens = dens 
		self.calc_size()
		self.gen_ind()
		self.allocate()
		self.set_data( (self.pts,self.bezy) )
		self.generate()

	def new( self , pos , which ) :
		if len(self) >= 3 or len(self.pts) > 0 : return

		Points.new( self , pos )

		if len(self) < 3 : return

		corners = []
		for p in self :
			corners.append( np.array(( p[0] , p[1] , p[2] )) )
		del self[:]

		corners.append( corners[2] + corners[0] - corners[1] )

		self.make_pts( corners )

		self.generate()

		self.get_geom().set_visibility( Bezier.CURVE , True )

	def find_pnt_index( self , pnt ) :
		for i in range(len(self.pts)) :
			if id(self.pts[i]) == id(pnt) :
				return i

	def move_current( self , v ) :
		if self.current == None :
			return

		if self.editmode == Points.PNT :
			self.current += v
		elif self.editmode == Points.ROW :
			sx = self.size[0]+3
			sy = self.size[1]+3
			ind = self.find_pnt_index( self.current )
			for i in range(ind%sx,sx*sy,sx) :
				self.pts[i] += v
		elif self.editmode == Points.COL :
			sx = self.size[0]+3
			ind = self.find_pnt_index( self.current )
			ind-= ind%sx
			for i in range(ind,ind+sx) :
				self.pts[i] += v

		self.generate()

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )

