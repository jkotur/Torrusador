from OpenGL.GL import *

import math as m
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

		#
		# generate indices for const u
		#

		lu = []
		lv = []
		lt = []
		for t in trimms :
			print t
			for p in t.get_intersections_v(dv) :
				print p
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
				lt.append( t )
		uarr = np.array( lu ) 
		varr = np.array( lv ) 

		ind = np.lexsort( (uarr,varr) )

		print 'sorted:'
		for i in ind :
			print uarr[i] , varr[i]
		print 'eos'

		trimms.sort( key = lambda t : t.min_v )

		for t in trimms : print t.min_v

		self.indx = []
		ends = []
		i = 1
		k = 0
		kb= 0
		eb= 0
		l = 0
		while i < len(ind) :
			u  = uarr[ind[i-1]]
			v  = varr[ind[i-1]]
			eu = uarr[ind[i  ]]
			ev = varr[ind[i  ]]
#            print u , v , '|' , eu , ev
			if v != ev :
				i+=1
				if k < eb :
					self.indx.insert(0,self.indx.pop())
					kb+=1
				k =kb
				continue

#            print v , k , l , len(self.indx)
			while l < len(trimms) and v >= trimms[l].beg_v :
				self.indx.insert(k,[])
				if not m.isinf(trimms[l].end_v) :
					ends.insert( 0 , trimms[l].end_v )
#                print v , trimms[l].beg_v , ends
				l+=1
				eb+=1
			while len(ends)>0 and v > ends[-1] :
#                print 'ends'
				ends.pop()
				kb+=1
			if k == len(self.indx) :
#                print 'append:' , k , kb , len(self.indx)
				self.indx.append([])
				eb+=1

			y = int(v / dv + .5)
			x = int(m.ceil(u / du ))
#            print u , v , '->' , x , y
			self.indx[k].append( x*sy+y )
			u += du
			while u <= eu :
				x = int(m.ceil(u / du ))
				self.indx[k].append( x*sy+y )
				self.indx[k].append( x*sy+y )
#                print u , v , '->' , x , y
				u += du
			self.indx[k].pop()
#            if m.isinf(lt[ind[i-1]].end_u) :
#                k+=1
#            else :
#                k-=1
			k+=1
			i+=1
#            print u , v , '--' , x , y
		for i in range(len(self.indx)) :
			self.indx[i] = np.array( self.indx[i] , np.uint32 )
#        for i in range(len(self.indx)) :
#            print '-->' , self.indx[i]

		#
		# generate indices for const u
		#

		lu = []
		lv = []
		lt = []
		for i in range(beg,end+1) :
#            print trimms[i]
			for p in trimms[i].get_intersections_u(du) :
#                print p
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
		uarr = np.array( lu ) 
		varr = np.array( lv ) 

		ind = np.lexsort( (varr,uarr) )

		self.indy = []
		i = 1
		while i < len(ind) :
			u  = uarr[ind[i-1]]
			v  = varr[ind[i-1]]
			eu = uarr[ind[i  ]]
			ev = varr[ind[i  ]]
#            print u , v , '|' , eu , ev
#            assert( v == ev )
			if u != eu :
				i+=1
				continue
			y = int(v / dv + .5)
			x = int(u / du + .5)
			self.indy.append( x*sy+y )
#            print u , v , '->' , x , y
			v += dv
			while v <= ev :
				y = int(v / dv + .5)
				self.indy.append( x*sy+y )
				self.indy.append( x*sy+y )
#                print u , v , '->' , x , y
				v += dv
			self.indy.append( x*sy+y )
			i+=2
#            print u , v , '--' , x , y
		self.indy = np.array( self.indy , np.uint32 )

		self.k = 0
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

