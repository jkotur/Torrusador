from OpenGL.GL import *

import math as m
import numpy as np

from trimming import TrimmingBorder

import csurf

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
			glDrawElements( GL_LINES , len(self.indy) , GL_UNSIGNED_INT , self.indy )
			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_points :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , pts )
			glDrawArrays(GL_POINTS, 0, len(pts)/3 )
			glDisableClientState(GL_VERTEX_ARRAY)


class SurfaceTrimmed( Surface ) :
	def __init__( self ) :
		Surface.__init__( self )

		self.k = 0

	def set_select( self , k ) :
		self.k = k 

	def gen_ind( self , sx , sy , maxu , maxv , trimms , beg = 0 , end = 1 ) :
		du = float(maxu) / (sx-1)
		dv = float(maxv) / (sy-1)

		lu = []
		lv = []
		for t in trimms :
			for p in t.get_intersections_v(dv) :
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
#                lu.append( p[0] )
#                lv.append( p[1] )

		vuarr = np.array( lu )
		vvarr = np.array( lv )

		lu = []
		lv = []
		for t in trimms :
			for p in t.get_intersections_u(du) :
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
#                lu.append( p[0] )
#                lv.append( p[1] )

		uuarr = np.array( lu )
		uvarr = np.array( lv )

#        du = round( du , 4 )
#        dv = round( dv , 4 )

		inu = np.lexsort( (vuarr,vvarr) )
		inv = np.lexsort( (uvarr,uuarr) )

		done = np.zeros((sx,sy,4),np.bool)

		addind = []
		adduv = []

		self.indx = []
		for ix in range(sx-1) :
			for iy in range(sy-1) :
				if any(done[ix,iy]) :
					continue
				niu = 0
				niv = 0

				while niu < len(inu) and round( vvarr[inu[niu]] / dv ) < iy+1 : niu+=1
				while vuarr[inu[niu+1]] < ix * du    : niu+=1
				while niv < len(inv) and round( uuarr[inv[niv]] / du ) < ix+1 : niv+=1
				while uvarr[inv[niv+1]] < iy * dv    : niv+=1

				stack = [ (ix,iy,niu,niv) ]
				self.indx.insert(0,[])
				addind.insert(0,[])
				adduv.insert(0,[])
				while len(stack) > 0 :
					x , y , iu , iv = stack.pop()

					u = float(x) * du
					v = float(y) * dv

					if x+1 < sx and u+du < vuarr[inu[iu+1]] - .1 :
						if not done[ x , y , 0 ] :
							done[ x   , y   , 0 ] = True
							done[ x+1 , y   , 1 ] = True
							self.indx[0].append(  x   *sy+y )
							self.indx[0].append( (x+1)*sy+y )
							if not all(done[ x+1 , y   ]) :
								niv = iv
								while round( uuarr[inv[niv  ]] / du ) < x+1 : niv+=1
								while uvarr[inv[niv+1]] < v    : niv+=1
								stack.append((x+1,y  , iu,niv))
					elif x+1 < sx :
						addind[0].append( x*sy+y )
						adduv[0].append( np.array( (vuarr[inu[iu+1]], v )))

					if x-1 >=0  and u-du > vuarr[inu[iu  ]] + .1 :
						if not done[ x , y , 1 ] :
							done[ x   , y   , 1 ] = True
							done[ x-1 , y   , 0 ] = True
							self.indx[0].append(  x   *sy+y )
							self.indx[0].append( (x-1)*sy+y )
							if not all(done[ x-1 , y   ]) :
								niv = iv
								while round( uuarr[inv[niv  ]] / du ) > x-1 : niv-=1
								while uvarr[inv[niv  ]] > v    : niv-=1
								stack.append((x-1,y  , iu,niv))
					elif x-1 >=0 :
						addind[0].append( x*sy+y )
						adduv[0].append( np.array( (vuarr[inu[iu  ]], v )))

					if y+1 < sy and v+dv < uvarr[inv[iv+1]] - .1 :
						if not done[ x , y   , 2 ] :
							done[ x , y   , 2 ] = True
							done[ x , y+1 , 3 ] = True
							self.indx[0].append(  x   *sy+y   )
							self.indx[0].append(  x   *sy+y+1 )
							if not all(done[ x   , y+1 ]) :
								niu = iu
								while round( vvarr[inu[niu  ]] / dv ) < y+1 : niu+=1
								while vuarr[inu[niu+1]] < u    : niu+=1
								stack.append((x  ,y+1,niu, iv))
					elif y+1 < sy :
						addind[0].append( x*sy+y )
						adduv[0].append( np.array( (u, uvarr[inv[iv+1]] )))

					if y-1 >=0  and v-dv > uvarr[inv[iv  ]] + .1 :
						if not done[ x , y , 3 ] :
							done[ x , y   , 3 ] = True
							done[ x , y-1 , 2 ] = True
							self.indx[0].append(  x   *sy+y   )
							self.indx[0].append(  x   *sy+y-1 )
							if not all(done[ x   , y-1 ]) :
								niu = iu
								while round( vvarr[inu[niu  ]] / dv ) > y-1 : niu-=1
								while vuarr[inu[niu  ]] > u     : niu-=1
								stack.append((x  ,y-1,niu, iv))
					elif y-1 >=0 :
						addind[0].append( x*sy+y )
						adduv[0].append( np.array( (u ,uvarr[inv[iv  ]] )))

		for i in range(len(self.indx)) :
			self.indx[i] = np.array( self.indx[i] , np.uint32 )

		return len(self.indx) , addind , adduv

	def draw_self( self , data ) :

		geom = data[1]

		pts = []
		for p in data[0] :
			pts.append(p[0])
			pts.append(p[1])
			pts.append(p[2])
		pts = np.array(pts,np.float32)

		addpts = data[2]

		floatsize = np.dtype(np.float32).itemsize

		if self.draw_curve :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , geom )
			if self.k == None :
				for k in range(len(self.indx)) :
					glDrawElements( GL_LINES, len(self.indx[k]), GL_UNSIGNED_INT ,self.indx[k] )
#                glVertexPointer( 3, GL_FLOAT , 0 , addpts[k] )
#                glDrawArrays( GL_LINES , 0 , len(addpts)* )
			elif len(self.indx) > self.k :
				glDrawElements( GL_LINES, len(self.indx[self.k]), GL_UNSIGNED_INT, self.indx[self.k] )
				glColor3f(0,1,0)
				glVertexPointer( 3, GL_FLOAT , 0 , addpts[self.k] )
				glDrawArrays( GL_LINES , 0 , len(addpts[self.k])*2 )
#                glVertexPointer( 3, GL_FLOAT , 0 , addpts[self.k] )
#                glDrawArrays( GL_LINES , 0 , len(addpts[self.k])/2 )
				glColor3f(1,1,1)

			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_points :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , pts )
			glDrawArrays(GL_POINTS, 0, len(pts)/3 )
			glDisableClientState(GL_VERTEX_ARRAY)

