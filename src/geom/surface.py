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

		#
		# generate indices for const u
		#
		lu = []
		lv = []
		lt = []
		# generate virtual curves for those which cut u=0 line
		# this code assumes that first trimming curve is border 
		# at min_u == 0
		trimms.sort( key = lambda t : t.sort_v )
		t = trimms[0]
		assert( isinstance(t,TrimmingBorder) )
		assert( t.min_u == 0 )
		endv = 0
		done = 2
		tid = 0
		tid0 = id(t)
		for p in t.get_intersections_v(dv) :
			if done < len(trimms) and p[1] > trimms[done].beg_v :
				if trimms[done].oneborder or m.isinf(trimms[done].beg_u) :
					tid = id(trimms[done])
					endv = trimms[done].end_v
				else :
					tid  = tid0
					tid0 = id(trimms[done])
					endv = trimms[done].beg_v

				l = len(lu)
				inv = True
				tu = []
				tv = []
				for p1 in trimms[done].get_intersections_v(dv) :
					tu.append( round(p1[0],4) )
					tv.append( round(p1[1],4) )
					lt.append( tid0 )
				if tv[0] < tv[-1] :
					lu += tu
					lv += tv
				else :
					lu += reversed(tu)
					lv += reversed(tv)
				done+=1
			if p[1] < endv :
				lu.insert(0,round(p[0],4))
				lv.insert(0,round(p[1],4))
				lt.insert(0,tid)
			else :
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
				lt.append( tid0 )

		for t in trimms[done:] :
			for p in t.get_intersections_v(dv) :
				lu.append( round(p[0],4) )
				lv.append( round(p[1],4) )
				lt.append( id(t) )

		for p in trimms[1].get_intersections_v(dv) :
			lu.append( round(p[0],4) )
			lv.append( round(p[1],4) )
			lt.append( id(t) )

		uarr = np.array( lu ) 
		varr = np.array( lv ) 

		n2l = np.lexsort( (uarr,varr) ) # normal to lexical order
		l2n = np.argsort( n2l )    # lexical to normal order

		print 'not sorted:'
		for i in range(len(varr)) :
			print  uarr[i] , varr[i] , lt[i]
		print 'eos'

		print 'sorted:'
		for i in n2l :
			print uarr[i] , varr[i] , lt[i]
		print 'eos'

		self.indx = []


		for i in range(0,len(lt)) :
			if i!=0 and lt[i-1] == lt[i] :
				continue
			active = [ (i,1) ] # FIXME: what if first dv is -1?
			self.indx.append([])
			while len(active) > 0 :
				#
				# get active point
				#
				i , sv = active.pop(0)
				sdv = np.sign(varr[i+sv] - varr[i])

				while i >= 0 and i < len(uarr)-1 :
					#
					# get corespondent point 
					#
					j  = n2l[l2n[i]+1] 

					u  = uarr[i]
					v  = varr[i]
					eu = uarr[j]
					ev = varr[j]

					#
					# if corespondent point is not on the same 
					# scanline continue loop (e.g. end of plane)
					#
					if v != ev :
						i+=sv
						continue

					#
					# check for new active point
					#
					prevvsin = nextvsin = None
					nj = j 
					xj = j
					while nj-1 >= 0 and lt[nj-1] == lt[nj] :
						prevvsin = np.sign( varr[nj  ] - varr[nj-1] )
						if prevvsin != 0 : break
						prevvsin = None
						nj-=1
					while xj+1 < len(varr) and lt[xj+1] == lt[xj] :
						nextvsin = np.sign( varr[xj+1] - varr[xj  ] )
						if nextvsin != 0 : break
						nextvsin = None
						xj+=1

					if j != i+sv and prevvsin != None and nextvsin != None :
						if prevvsin != nextvsin :
							if uarr[nj] < uarr[xj] :
								active.append( (xj,+1) )
							else :
								active.append( (nj,-1) )

					#
					# draw scanline
					#
					y = int(v / dv + .5)
					x = int(m.ceil(u / du ))
					self.indx[-1].append( x*sy+y )
					u += du
					while u <= eu :
						x = int(m.ceil(u / du ))
						self.indx[-1].append( x*sy+y )
						self.indx[-1].append( x*sy+y )
						u += du
					self.indx[-1].pop()

					#
					# check for field end, break if:
					# * line is going backward
					# * next point is on another line 
					# * line was drawn to next point of the same curve (dead end)
					#
					if np.sign(varr[i+sv]-varr[i]) != sdv or \
					   lt[i] != lt[i+sv] or \
					   j == i+sv :
						break
					sdv = np.sign(varr[i+sv] - varr[i])

					#
					# get next point 
					#
					i+=sv

		for i in range(len(self.indx)) :
			self.indx[i] = np.array( self.indx[i] , np.uint32 )
		for i in range(len(self.indx)) :
			print '-->' , self.indx[i]

		self.k = 0
		return len(self.indx)

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

