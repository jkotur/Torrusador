
cimport numpy as np

import cython

import random as rnd
import math as m

from copy import copy

import numpy as np
import scipy as sp
import scipy.optimize as op
from scipy import interpolate
import scipy.spatial.distance as dist

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void decasteljau( np.ndarray[ float , ndim=1 ] pts , float t ,
		  np.ndarray[ float , ndim=1 ] out , int id , int len ) :
	if len <= 0 :
		return 

	cdef int k = 0
	cdef int i = 0

	k = len-1
	while k>=0 :
		for i in range(0,k*3,3) :
			pts[i  ] = pts[i  ]*(1.0-t) + pts[i+3]*t
			pts[i+1] = pts[i+1]*(1.0-t) + pts[i+4]*t
			pts[i+2] = pts[i+2]*(1.0-t) + pts[i+5]*t
		k -= 1
	out[id  ] = pts[0]
	out[id+1] = pts[1]
	out[id+2] = pts[2]

@cython.cdivision(True)
cdef rekN( int n , int i , double t ) :
	if n == 0 : return 1 if t >= i and t < i + 1 else 0
	cdef double n1 = rekN(n - 1, i, t)
	cdef double n2 = rekN(n - 1, i + 1, t)
	return n1 * <double>(t - i) / <double>(n) + n2 * <double>(i + n + 1 - t) / <double>(n)

cpdef bspline_surf( double u , double v , np.ndarray[ double , ndim=3 ] pts ) : 
	''' calculates (x,y,z) of bezier surface in point (u,v) for uniform parametrization '''
	cdef int i
	cdef double n
	cdef np.ndarray[ double , ndim=1 ] q0 , q1 , q2 ,q3
	q0 = np.zeros(3,np.double)
	q1 = np.zeros(3,np.double)
	q2 = np.zeros(3,np.double)
	q3 = np.zeros(3,np.double)

	cdef int xoff = int( u ) 
	cdef int yoff = int( v )

	if xoff == pts.shape[0] - 3 : 
		xoff-= 1
	if yoff == pts.shape[1] - 3 :
		yoff-= 1

	u = u - xoff + 3.0
	v = v - yoff + 3.0

	if u > 4.0 or v > 4.0 : return np.zeros(3,np.double)

	for i in range(4) :
		n = rekN( 3 , i , u )
		q0 += pts[xoff+i,yoff+0] * n
		q1 += pts[xoff+i,yoff+1] * n 
		q2 += pts[xoff+i,yoff+2] * n 
		q3 += pts[xoff+i,yoff+3] * n 

	cdef np.ndarray[ double , ndim=1 ] res = np.zeros(3,np.double)

	res  = rekN( 3 , 0 , v ) * q0
	res += rekN( 3 , 1 , v ) * q1
	res += rekN( 3 , 2 , v ) * q2
	res += rekN( 3 , 3 , v ) * q3

	return res

cpdef bspline_surf_prime_v( double u , double v , np.ndarray[ double , ndim=3 ] pts ) :
	cdef int i
	cdef double n
	cdef np.ndarray[ double , ndim=1 ] q0 , q1 , q2 ,q3
	q0 = np.zeros(3,np.double)
	q1 = np.zeros(3,np.double)
	q2 = np.zeros(3,np.double)
	q3 = np.zeros(3,np.double)

	cdef int xoff = int( u ) 
	cdef int yoff = int( v )

	if xoff == pts.shape[0] - 3 : 
		xoff-= 1
	if yoff == pts.shape[1] - 3 :
		yoff-= 1

	u = u - xoff + 3.0
	v = v - yoff + 3.0

	if u > 4.0 or v > 4.0 : return np.zeros(3,np.double)

	for i in range(4) :
		n = rekN( 3 , i , u )
		q0 += pts[xoff+i,yoff+0] * n
		q1 += pts[xoff+i,yoff+1] * n 
		q2 += pts[xoff+i,yoff+2] * n 
		q3 += pts[xoff+i,yoff+3] * n 
	
	q0 = q1 - q0
	q1 = q2 - q1
	q2 = q3 - q2

	cdef np.ndarray[ double , ndim=1 ] res = np.zeros(3,np.double)

	res  = rekN( 2 , 1 , v ) * q0
	res += rekN( 2 , 2 , v ) * q1
	res += rekN( 2 , 3 , v ) * q2

	return res

cpdef bspline_surf_prime_u( double u , double v , np.ndarray[ double , ndim=3 ] pts ) :
	cdef int i
	cdef double n
	cdef np.ndarray[ double , ndim=1 ] q0 , q1 , q2 ,q3
	q0 = np.zeros(3,np.double)
	q1 = np.zeros(3,np.double)
	q2 = np.zeros(3,np.double)
	q3 = np.zeros(3,np.double)

	cdef int xoff = int( u ) 
	cdef int yoff = int( v )

	if xoff == pts.shape[0] - 3 : 
		xoff-= 1
	if yoff == pts.shape[1] - 3 :
		yoff-= 1

	u = u - xoff + 3.0
	v = v - yoff + 3.0

	if u > 4.0 or v > 4.0 : return np.zeros(3,np.double)

	for i in range(4) :
		n = rekN( 3 , i , v )
		q0 += pts[xoff+0,yoff+i] * n
		q1 += pts[xoff+1,yoff+i] * n 
		q2 += pts[xoff+2,yoff+i] * n 
		q3 += pts[xoff+3,yoff+i] * n 
	
	q0 = q1 - q0
	q1 = q2 - q1
	q2 = q3 - q2

	cdef np.ndarray[ double , ndim=1 ] res = np.zeros(3,np.double)

	res  = rekN( 2 , 1 , u ) * q0
	res += rekN( 2 , 2 , u ) * q1
	res += rekN( 2 , 3 , u ) * q2

	return res

def diff_surfs( p , p1 , p2 ) :
	a = bspline_surf( p[0], p[1], p1 ) - bspline_surf( p[2], p[3], p2 )
	return a[0]*a[0] + a[1]*a[1] + a[2]*a[2]

def diff_grad( p , p1 , p2 ) :
	a = bspline_surf        ( p[0], p[1], p1 ) - bspline_surf        ( p[2], p[3], p2 )
	b = bspline_surf_prime_u( p[0], p[1], p1 )
	c = bspline_surf_prime_v( p[0], p[1], p1 )
	d =-bspline_surf_prime_u( p[2], p[3], p2 )
	e =-bspline_surf_prime_v( p[2], p[3], p2 )
	return np.array((
		2*a[0]*b[0] + 2*a[1]*b[1] + 2*a[2]*b[2] ,
		2*a[0]*c[0] + 2*a[1]*c[1] + 2*a[2]*c[2] ,
		2*a[0]*d[0] + 2*a[1]*d[1] + 2*a[2]*d[2] ,
		2*a[0]*e[0] + 2*a[1]*e[1] + 2*a[2]*e[2] )) * 10

def printer( x ) : print x

def cut_bsplines( np.ndarray[ double , ndim=3 ] a , np.ndarray[ double , ndim=3 ] b , beg ) :
	res = op.fmin_cg( diff_surfs , np.array((.5,.5,.5,.5)) , args = (a,b) , fprime = diff_grad ,
			maxiter = 2048 )# , callback = printer )
	print res
	return res

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void split_bezier( np.ndarray[ float , ndim=2 ] pts , int ioffset , np.ndarray[ float , ndim=2 ] out , int l , int ooffset , int stride ) :
	cdef int k = 0
	cdef int i = 0

	cdef int idi = ioffset
	cdef int ido = ooffset

	cdef float t = 0.5

	k = l-1
	while k>=0 :
		out[ido] = pts[idi]
		for i in range(0,k,1) :
			pts[idi+i  ] = pts[idi+i  ]*(1.0-t) + pts[idi+i+1]*t
		ido+= stride
		k  -= 1

@cython.boundscheck(False)
@cython.cdivision(True)
cpdef int split_bezier_surf( pts , np.ndarray[ float , ndim=2 ] out ) :
	cdef np.ndarray[ float , ndim=2 ] rows = np.zeros( (4*4,3) , np.float32 )

	cdef np.ndarray[ float , ndim=2 ] row = np.empty( (4,3) , np.float32 )
	cdef np.ndarray[ float , ndim=2 ] tmp = np.empty( (4,3) , np.float32 )

	cdef int j 
	cdef int i

	for j in range(4) :
		for i in range(4) :
			row[i] = pts[j+i*4]
		for i in range(4) : tmp[i] = row[i]
		split_bezier( tmp , 0 , rows , 4 , j , 4 )

	for j in range(2) :
		split_bezier( rows , j*4 , out , 4 , j*4 , 1 )
	for j in range(2) :
		for i in range(4) : tmp[(4-i-1)  ] = rows[(j*4+i)  ]
		for i in range(4) : out[(j+2)*4+i] = tmp[i]

	return 0

@cython.boundscheck(False)
@cython.cdivision(True)
cpdef gen_bezier( pts , np.ndarray[ float , ndim=1 ] bezx , np.ndarray[ float , ndim=1 ] bezy
		, int zx , int zy , int sx , int sy , int dx , int dy ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id
	cdef int idi
	cdef int i3

	cdef int y
	cdef int x

	cdef int i
	cdef int j

	cdef float t
	cdef float dt

	cdef np.ndarray[ float ] tmp = np.empty( 4*3 , np.float32 )
	cdef np.ndarray[ float ] tmp2= np.empty( 4*3 , np.float32 )

	for y in range(0,sy,dy) :
		px = 0
		x  = 0
		while x < sx-1 :
			id = px+py*(zx*3+1)
			tmp[0: 3] = pts[id  ][:]
			tmp[3: 6] = pts[id+1][:]
			tmp[6: 9] = pts[id+2][:]
			tmp[9:12] = pts[id+3][:]
			id = x+y*sx
			j = 0
			t = 0
			dt= 1.0/(dx*3)
			while t <= 1.001 :
				i3 = (id+j)*3
				for i in range(12) : tmp2[i] = tmp[i]
				decasteljau( tmp2 , t , bezx , i3 , 4 )
				j+=1
				t+=dt
			px += 3
			x  += dx*3
		py += 1

	for x in range(sx) :
		y = 0
		while y < sy-1 :
			id = y+x*sy
			for i in range(4) :
				idi = (x+(y/dy+i)*dy*sx)*3
				i3  = i*3
				tmp[i3  ] = bezx[idi  ]
				tmp[i3+1] = bezx[idi+1]
				tmp[i3+2] = bezx[idi+2]
			j = 0 
			t = 0
			dt= 1.0/(dy*3)
			while t <= 1.001 :
				i3 = (id+j)*3
				for i in range(12) : tmp2[i] = tmp[i]
				decasteljau( tmp2 , t , bezy , i3 , 4 )
				j+=1
				t+=dt
			y+=dy*3

	return bezx , bezy

@cython.boundscheck(False)
@cython.cdivision(True)
cpdef gen_deboor( pts , np.ndarray[ float , ndim=1 ] bezx , np.ndarray[ float , ndim=1 ] bezy
		, int zx , int zy , int sx , int sy , int dx , int dy
		, np.ndarray[ float ] N ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id

	cdef int y
	cdef int x

	cdef int j
	cdef float k , dk

	cdef int l
	cdef int idj
	cdef int ik

	cdef np.ndarray[ float ] tmp = np.empty( 4*3 , np.float32 )

	for y in range(zy+3) :
		px = 0
		x  = 0
		while x < sx-1 :
			id = px+py*(zx+3)
			tmp[0: 3] = pts[id  ][:]
			tmp[3: 6] = pts[id+1][:]
			tmp[6: 9] = pts[id+2][:]
			tmp[9:12] = pts[id+3][:]
			id = x+y*dy*sx
			j = 0
			k = 0
			dk = 256.0;
			dk/= float(dx*3);
			while k < 256.1 :
				ik = int(k/4.0+.5);
				ik*= 4;
				idj = (id+j)*3
				bezx[idj  ] = 0
				bezx[idj+1] = 0
				bezx[idj+2] = 0
				for l in range(4) :
					bezx[idj  ] += tmp[l*3  ] * N[ik+l]
					bezx[idj+1] += tmp[l*3+1] * N[ik+l]
					bezx[idj+2] += tmp[l*3+2] * N[ik+l]
				j+=1
				k+=dk
			x  += dx*3
			px += 1
		py += 1

	cdef int i
	
	for x in range(sx) :
		py = 0
		for y in range(zy) :
			id = y*3*dy+x*sy
			for i in range(4) :
				tmp[i*3  ] = bezx[(x+(y+i)*dy*sx)*3  ]
				tmp[i*3+1] = bezx[(x+(y+i)*dy*sx)*3+1]
				tmp[i*3+2] = bezx[(x+(y+i)*dy*sx)*3+2]
			j = 0
			k = 0
			dk = 256.0;
			dk/= float(dy*3);
			while k < 256.1 :
				ik = int(k/4.0+.5);
				ik*= 4;
				idj = (id+j)*3
				bezy[idj  ] = 0
				bezy[idj+1] = 0
				bezy[idj+2] = 0
				for l in range(4) :
					bezy[idj  ] += tmp[l*3  ] * N[ik+l]
					bezy[idj+1] += tmp[l*3+1] * N[ik+l]
					bezy[idj+2] += tmp[l*3+2] * N[ik+l]
				j+=1
				k+=dk
	return bezx , bezy

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void F0( np.ndarray[ float , ndim=1 ] pts , int i , 
		  np.ndarray[ float , ndim=1 ] fa , np.ndarray[ float , ndim=1 ] fb ,
		  float u , float v ) :
	pts[i  ] = (u*fa[0]+v*fb[0])/(u+v)
	pts[i+1] = (u*fa[1]+v*fb[1])/(u+v)
	pts[i+2] = (u*fa[2]+v*fb[2])/(u+v)

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void F1( np.ndarray[ float , ndim=1 ] pts , int i , 
		  np.ndarray[ float , ndim=1 ] fa , np.ndarray[ float , ndim=1 ] fb ,
		  float u , float v ) :
	pts[i  ] = ((1-u)*fb[0]+v*fa[0])/(1-u+v)
	pts[i+1] = ((1-u)*fb[1]+v*fa[1])/(1-u+v)
	pts[i+2] = ((1-u)*fb[2]+v*fa[2])/(1-u+v)

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void F2( np.ndarray[ float , ndim=1 ] pts , int i , 
		  np.ndarray[ float , ndim=1 ] fa , np.ndarray[ float , ndim=1 ] fb ,
		  float u , float v ) :
	pts[i  ] = ((1-u)*fa[0]+(1-v)*fb[0])/(2-u-v)
	pts[i+1] = ((1-u)*fa[1]+(1-v)*fb[1])/(2-u-v)
	pts[i+2] = ((1-u)*fa[2]+(1-v)*fb[2])/(2-u-v)

@cython.boundscheck(False)
@cython.cdivision(True)
cdef void F3( np.ndarray[ float , ndim=1 ] pts , int i , 
		  np.ndarray[ float , ndim=1 ] fa , np.ndarray[ float , ndim=1 ] fb ,
		  float u , float v ) :
	pts[i  ] = (u*fb[0]+(1-v)*fa[0])/(1+u-v)
	pts[i+1] = (u*fb[1]+(1-v)*fa[1])/(1+u-v)
	pts[i+2] = (u*fb[2]+(1-v)*fa[2])/(1+u-v)

@cython.boundscheck(False)
@cython.cdivision(True)
cpdef gen_gregory( pts , np.ndarray[ float , ndim=1 ] bezx , np.ndarray[ float , ndim=1 ] bezy
		, int zx , int zy , int sx , int sy , int dx , int dy ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id
	cdef int idi
	cdef int i3

	cdef int y
	cdef int x

	cdef int i
	cdef int j

	cdef float t
	cdef float dt

	cdef float u
	cdef float v

	cdef np.ndarray[ float ] tmp = np.empty( 4*3 , np.float32 )
	cdef np.ndarray[ float ] tmp2= np.empty( 4*3 , np.float32 )

	assert( zx == 1 )
	assert( zy == 1 )

	for y in range(0,sy,dy) :
		px = 0
		x  = 0
		while x < sx-1 :
			id = px+py*(zx*3+1)
			tmp[0: 3] = pts[id  ][:]
			tmp[3: 6] = pts[id+1][:]
			tmp[6: 9] = pts[id+2][:]
			tmp[9:12] = pts[id+3][:]
			id = x+y*sx
			j = 0
			t = 0
			dt= 1.0/(dx*3)
			while t <= 1.001 :

				u = t
				v = 1.0/3.0
				if py == 1 :
					F0( tmp , 3 , pts[ 5] , pts[ 6] , u , v )
					F1( tmp , 6 , pts[ 9] , pts[10] , u , v )
				elif py == 2 :
					F2( tmp , 3 , pts[16] , pts[17] , u , v )
					F3( tmp , 6 , pts[18] , pts[19] , u , v )

				for i in range(12) : tmp2[i] = tmp[i]
				decasteljau( tmp2 , t , bezx , (id+j)*3 , 4 )
				j+=1
				t+=dt
			px += 3
			x  += dx*3
		py += 1

	for x in range(sx) :
		y = 0
		while y < sy-1 :
			id = y+x*sy
			for i in range(4) :
				idi = (x+(y/dy+i)*dy*sx)*3
				i3  = i*3
				tmp[i3  ] = bezx[idi  ]
				tmp[i3+1] = bezx[idi+1]
				tmp[i3+2] = bezx[idi+2]
			j = 0 
			t = 0
			dt= 1.0/(dy*3)
			while t <= 1.001 :
				i3 = (id+j)*3
				for i in range(12) : tmp2[i] = tmp[i]
				decasteljau( tmp2 , t , bezy , i3 , 4 )
				j+=1
				t+=dt
			y+=dy*3

	return bezx , bezy

def center( p0 , pts ) :
	return [ dist.euclidean(p,p0) for p in pts ]

def fill_gap_c0( surfs , subsurfs , snum ) :
	pts = [ s.get_pts() for s in surfs[snum:] ]

	q = np.empty( (snum,3) , np.float32 )

	for i in range(snum) :
		split_bezier_surf( surfs[i].get_pts() , subsurfs[i] )

	for i in range(snum) :
		pts[i][ 1] = subsurfs[i-1,  9]
		pts[i][ 2] = subsurfs[i-1, 10]
		pts[i][ 3] = subsurfs[i-1, 11]
		pts[i][ 0] = subsurfs[i  ,  0]
		pts[i][ 4] = subsurfs[i  ,  1]
		pts[i][ 8] = subsurfs[i  ,  2]
		pts[i][12] = subsurfs[i  ,  3]

		pts[i][ 6] = 2*pts[i][ 1] - subsurfs[i-1,13]
		pts[i][ 9] = 2*pts[i][ 2] - subsurfs[i-1,14]
		pts[i][ 7] = 2*pts[i][ 3] - subsurfs[i-1,15]
                                                
		pts[i][ 5] = 2*pts[i][ 4] - subsurfs[i  , 5]
		pts[i][17] = 2*pts[i][ 8] - subsurfs[i  , 6]
		pts[i][13] = 2*pts[i][12] - subsurfs[i  , 7]

		pts[i][10] = pts[i][ 9]
		pts[i][16] = pts[i][17]
		
		q[i] = (3.0*pts[i][7]-1.0*pts[i][3])/2.0

	p0 = np.mean(q,0)
	p0 ,  err = op.leastsq( center , p0 , q )

	if err > 4 :
		print 'leastsq err' , err
		p0 = np.mean(q,0)

	for i in range(snum) :
		pts[i][15] = p0
		pts[i][11] = (2.0*q[i]+p0)/3.0

	for i in range(snum) :
		pts[i-1][14] = pts[i][11]

	x = [ 0.0 , 1.0 , 3.0 ]
	for i in range(snum) :
		y = np.array(
				( pts[i][ 2]-pts[i][ 3] ,
				  pts[i][10]-pts[i][ 7] ,
				  pts[i][14]-pts[i][15] ) , np.float32 )
		pts[i][18] = pts[i][11] + interpolate.interp1d( x , y , 'quadratic' , 0 , False )(2.0)
		pts[i][18] = np.array( pts[i][18] , np.float32 )
		y = np.array(
				( pts[i][ 8]-pts[i][12] ,
				  pts[i][16]-pts[i][13] ,
				  pts[i][11]-pts[i][15] ) , np.float32 )
		pts[i][19] = pts[i][14] + interpolate.interp1d( x , y , 'quadratic' , 0 , False )(2.0)
		pts[i][19] = np.array( pts[i][19] , np.float32 )

	return pts

def fill_gap_c1( surfs , subsurfs , snum ) :
	pts = fill_gap_c0( surfs , subsurfs , snum )

	surfs[0                ].get_pts()[4] = 3*pts[0][0]-2*pts[0][1]
	surfs[snum-1].get_pts()[7] = 3*pts[0][0]-2*pts[0][4]
	for i in range(1,snum) :
		surfs[i  ].get_pts()[4] = 3*pts[i][0]-2*pts[i][1]
		surfs[i-1].get_pts()[7] = 3*pts[i][0]-2*pts[i][4]

	return pts

def fill_gap_c2( surfs , subsurfs , snum ) :
	pts = fill_gap_c1( surfs , subsurfs , snum )

	for i in range(snum) :
		p = surfs[i].get_pts()
		p[6] = p[7]+p[2]-p[3]
		p[5] = p[4]+p[1]-p[0]

