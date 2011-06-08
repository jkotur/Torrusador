from OpenGL.GL import *

import math as m
import numpy as np

from trimming import TrimmingBorder

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

		print uuarr

		inu = np.lexsort( (vuarr,vvarr) )
		inv = np.lexsort( (uvarr,uuarr) )

		print '--> u'
		for i in inu : print vuarr[i] , vvarr[i] 
		print '--> v'
		for i in inv : print uuarr[i] , uvarr[i] 

#        stack = [ (0,5,20 if len(inu)>20 else 0,0) ]
		stack = [ (0,0,0,0) ]
		done = np.zeros((sx,sy,4),np.bool)

		self.indx = [[]]
		self.indy = [[]]
		while len(stack) > 0 :
			x , y , iu , iv = stack.pop()

			u = float(x) * du
			v = float(y) * dv

			print  x , y , '\t|\t', u , v , '\t|\t' , iu , iv , '\t|\t' , vuarr[inu[iu]] , vvarr[inu[iu]] , '\t|\t' , uuarr[inv[iv]] , uvarr[inv[iv]] 

			if x+1 < sx and u+du < vuarr[inu[iu+1]] :
				if not done[ x , y , 0 ] :
					done[ x   , y   , 0 ] = True
					done[ x+1 , y   , 1 ] = True
					self.indx[0].append(  x   *sy+y )
					self.indx[0].append( (x+1)*sy+y )
					if not all(done[ x+1 , y   ]) :
						niv = iv
						while uuarr[inv[niv  ]] < u+du : niv+=1
						while uvarr[inv[niv+1]] < v    : niv+=1
						print '  ->',  x+1 , y
						stack.append((x+1,y  , iu,niv))
			if x-1 >=0  and u-du > vuarr[inu[iu  ]] :
				if not done[ x , y , 1 ] :
					done[ x   , y   , 1 ] = True
					done[ x-1 , y   , 0 ] = True
					self.indx[0].append(  x   *sy+y )
					self.indx[0].append( (x-1)*sy+y )
					if not all(done[ x-1 , y   ]) :
						niv = iv
						while uuarr[inv[niv  ]] > u-du : niv-=1
						while uvarr[inv[niv  ]] > v    : niv-=1
						print '  ->' , x-1 , y
						stack.append((x-1,y  , iu,niv))
			if y+1 < sy and v+dv < uvarr[inv[iv+1]] :
				if not done[ x , y   , 2 ] :
					done[ x , y   , 2 ] = True
					done[ x , y+1 , 3 ] = True
					self.indx[0].append(  x   *sy+y   )
					self.indx[0].append(  x   *sy+y+1 )
					if not all(done[ x   , y+1 ]) :
						niu = iu
						while vvarr[inu[niu  ]] < v+dv : niu+=1
						while vuarr[inu[niu+1]] < u    : niu+=1
						print '  ->' , x   , y+1
						stack.append((x  ,y+1,niu, iv))
			if y-1 >=0  and v-dv > uvarr[inv[iv  ]] :
				if not done[ x , y , 3 ] :
					done[ x , y   , 3 ] = True
					done[ x , y-1 , 2 ] = True
					self.indx[0].append(  x   *sy+y   )
					self.indx[0].append(  x   *sy+y-1 )
					if not all(done[ x   , y-1 ]) :
						niu = iu
						print '  ->' , x   , y-1
						while vvarr[inu[niu  ]] > v-dv : niu-=1
						while vuarr[inu[niu  ]] > u    : niu-=1
						stack.append((x  ,y-1,niu, iv))

		for i in range(len(self.indx)) :
			self.indx[i] = np.array( self.indx[i] , np.uint32 )
		for i in range(len(self.indy)) :
			self.indy[i] = np.array( self.indy[i] , np.uint32 )

		return len(self.indx)

	def draw_self( self , data ) :

		geom = data[1]

		pts = []
		for p in data[0] :
			pts.append(p[0])
			pts.append(p[1])
			pts.append(p[2])
		pts = np.array(pts,np.float32)

		if self.draw_curve :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , geom )
			if self.k == None :
				for k in range(len(self.indx)) :
					glDrawElements( GL_LINES, len(self.indx[k]), GL_UNSIGNED_INT ,self.indx[k] )
			elif len(self.indx) > self.k :
				glDrawElements( GL_LINES, len(self.indx[self.k]), GL_UNSIGNED_INT, self.indx[self.k] )
#            glDrawElements( GL_LINES , len(self.indy) , GL_UNSIGNED_INT , self.indy[0] )
			glDisableClientState(GL_VERTEX_ARRAY)

		if self.draw_points :
			glEnableClientState(GL_VERTEX_ARRAY)
			glVertexPointer( 3, GL_FLOAT , 0 , pts )
			glDrawArrays(GL_POINTS, 0, len(pts)/3 )
			glDisableClientState(GL_VERTEX_ARRAY)

