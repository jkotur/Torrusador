
cimport numpy as np

import cython

import random as rnd
import math as m

from copy import copy

import numpy as np

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

#@cython.boundscheck(False)
#@cython.cdivision(True)
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
