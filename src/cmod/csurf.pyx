
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

cpdef gen_deboor( pts , bezx , bezy , int zx , int zy , int sx , int sy , int dx , int dy
		, np.ndarray[ float ] N ) :
	return gen_bezier( pts , bezx , bezy , zx , zy , sx , sy , dx , dy )
