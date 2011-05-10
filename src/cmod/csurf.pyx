
cimport numpy as np

import cython

import random as rnd
import math as m

from copy import copy

import numpy as np

@cython.boundscheck(False)
cdef decasteljau( np.ndarray[ float , ndim=1 ] pts , float t ) :
	if len(pts) <= 0 :
		return 0

	cdef int k = 0
	cdef int i = 0

#        for k in reversed(range(0,len(pts)/3)) :
	k = len(pts)/3-1
	while k>=0 :
		for i in range(0,k*3,3) :
			pts[i  ] = pts[i  ]*(1.0-t) + pts[i+3]*t
			pts[i+1] = pts[i+1]*(1.0-t) + pts[i+4]*t
			pts[i+2] = pts[i+2]*(1.0-t) + pts[i+5]*t
		k -= 1
	return pts[0:3]

@cython.boundscheck(False)
cpdef gen_bezier( pts , np.ndarray[ float , ndim=1 ] bezx , np.ndarray[ float , ndim=1 ] bezy
		, int zx , int zy , int sx , int sy , int dx , int dy ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id

	cdef int y
	cdef int x

	cdef int j

	cdef np.ndarray[ float ] tmp = np.empty( 4*3 , np.float32 )

	for y in range(0,sy,dy) :
		px = 0
		for x in range(0,sx-1,dx*3):
			id = px+py*(zx*3+1)
			tmp[0: 3] = pts[id  ][:]
			tmp[3: 6] = pts[id+1][:]
			tmp[6: 9] = pts[id+2][:]
			tmp[9:12] = pts[id+3][:]
			id = x+y*sx
			j = 0
			for t in np.linspace(0,1,dx*3+1) :
				bezx[(id+j)*3:(id+j)*3+3] = decasteljau( copy(tmp) , t )
				j+=1
			px += 3
		py += 1

	cdef int i

	for x in range(sx) :
		for y in range(0,sy-1,dy*3) :
			id = y+x*sy
			for i in range(4) :
				tmp[i*3  ] = bezx[(x+(y/dy+i)*dy*sx)*3  ]
				tmp[i*3+1] = bezx[(x+(y/dy+i)*dy*sx)*3+1]
				tmp[i*3+2] = bezx[(x+(y/dy+i)*dy*sx)*3+2]
			j = 0 
			for t in np.linspace(0,1,dy*3+1) :
				bezy[(id+j)*3:(id+j)*3+3] = decasteljau( copy(tmp) , t )
				j+=1

	return bezx , bezy

@cython.boundscheck(False)
cpdef gen_deboor( pts , bezx , bezy , int zx , int zy , int sx , int sy , int dx , int dy
		, np.ndarray[ float ] N ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id

	cdef int y
	cdef int x

	cdef int j
	cdef float k , dk

	cdef np.ndarray[ float ] tmp = np.empty( 4*3 , np.float32 )

	for y in range(zy+3) :
		px = 0
		for x in range(0,sx-1,dx*3):
			id = px+py*(zx+3)
			tmp[0: 3] = pts[id  ][:]
			tmp[3: 6] = pts[id+1][:]
			tmp[6: 9] = pts[id+2][:]
			tmp[9:12] = pts[id+3][:]
			id = x+y*dy*sx
			j = 0
			k = 0
			dk = float(256)/float(dx*3);
			while k < 256.1 :
				ik = int(k/4.0+.5)*4;
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
			dk = float(256)/float(dy*3);
			while k < 256.1 :
				ik = int(k/4.0+.5)*4;
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

