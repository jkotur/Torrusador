from OpenGL.GL import *

import numpy as np

from curve import Curve

class Surface( Curve ) :

	def __init__( self ) :
		Curve.__init__(self)

	def gen_ind( self , sx , sy ) :
		self.indx = []
		for x in range(sx) :
			for y in range(sy-1) :
				self.indx.append( x*sy+y )
				self.indx.append( x*sy+1+y )
		self.indx = np.array( self.indx , np.uint32 )

		self.indy = []
		for y in range(sy) :
			for x in range(sx-1) :
				self.indy.append( x*sy+y )
				self.indy.append( (x+1)*sy+y )
		self.indy = np.array( self.indy , np.uint32 )

	def gfx_init( self ) :
		pass

	def draw_self( self , data ) :

		geom = data[1]
#                geom = []
#                for p in data[1] :
#                        geom.append(p[0])
#                        geom.append(p[1])
#                        geom.append(p[2])
#                geom = np.array(geom,np.float32)

		pts = []
		for p in data[0] :
			pts.append(p[0])
			pts.append(p[1])
			pts.append(p[2])
		pts = np.array(pts,np.float32)

		if self.draw_curve :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , geom )
			glDrawElements( GL_LINES , len(self.indx) , GL_UNSIGNED_INT , self.indx )
#            glDrawElements( GL_LINES , len(self.indy) , GL_UNSIGNED_INT , self.indy )
			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_points :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , pts )
			glDrawArrays(GL_POINTS, 0, len(pts)/3 )
			glDisableClientState(GL_VERTEX_ARRAY)


class SurfaceTrimmed( Surface ) :
	def __init__( self ) :
		Surface.__init__( self )

	def gen_ind( self , sx , sy , maxu , maxv , trimms , beg = 0 , end = 1 ) :
		du = float(maxu) / (sx-1)
		dv = float(maxv) / (sy-1)

		lu = []
		lv = []
		for i in range(beg,end+1) :
			print trimms[i]
			for p in trimms[i].get_intersections_v(dv) :
				print p
				lu.append( p[0] )
				lv.append( p[1] )
		uarr = np.array( lu ) 
		varr = np.array( lv ) 

		ind = np.lexsort( (uarr,varr) )

		for i in ind :
			print uarr[i] , varr[i]

		self.indx = []
		for i in range(1,len(ind),2) :
			u  = uarr[ind[i-1]]
			v  = varr[ind[i-1]]
			eu = uarr[ind[i  ]]
			ev = varr[ind[i  ]]
			print u , v , '|' , eu , ev
#            assert( v == ev )
			if v != ev : continue
			y = int(v / dv + .5)
			x = int(u / du + .5)
			self.indx.append( x*sy+y )
			print u , v , '->' , x , y
			u += du
			while u <= eu :
				x = int(u / du + .5)
				self.indx.append( x*sy+y )
				self.indx.append( x*sy+y )
				print u , v , '->' , x , y
				u += du
			self.indx.append( x*sy+y )
			print u , v , '--' , x , y
		self.indx = np.array( self.indx , np.uint32 )

		self.indy = []
		self.indy = np.array( self.indy , np.uint32 )


