
cimport numpy as np

import cython

import random as rnd
import math as m

from copy import copy

import numpy as np

cdef decasteljau( pts , float t ) :
	if len(pts) <= 0 :
		return 0

	for k in reversed(range(0,len(pts))) :
		for i in range(k) :
			pts[i] = pts[i]*(1.0-t) + pts[i+1]*t
	return pts[0]

cpdef generate( pts , bezx , bezy , int zx , int zy , int sx , int sy , int dx , int dy ) :
	cdef int px = 0
	cdef int py = 0
	cdef int id

	cdef int y
	cdef int x

	cdef int j

	for y in range(0,sy,dy) :
		px = 0
		for x in range(0,sx-1,dx*3):
			id = px+py*(zx*3+1)
			tmp = pts[id:id+4]
			id = x+y*sx
			j = 0
			for t in np.linspace(0,1,dx*3+1) :
				bezx[id+j] = decasteljau( copy(tmp) , t )
				j+=1
			px += 3
		py += 1

	cdef int i

	tmp = [0,0,0,0] 
	for x in range(sx) :
		for y in range(0,sy-1,dy*3) :
			id = y+x*sy
			tmp[0] = bezx[x+(y/dy  )*dy*sx]
			for i in range(4) :
				tmp[i] = bezx[x+(y/dy+i)*dy*sx]
			j = 0 
			for t in np.linspace(0,1,dy*3+1) :
				bezy[id+j] = decasteljau( copy(tmp) , t )
				j+=1

	return bezx , bezy

