
import numpy as np

import scipy.linalg as sla

from look.node import Node
from geom.point import Point

from points import Points

from geom.bspline import Bspline
from geom.bezier import Bezier
from geom.dummy import Dummy
from geom.curve import Curve

class Interpolation( Points ) :
	Mpb = np.array( [[ 1 ,    1    ,    1    , 1 ]
	              ,  [ 0 , 1.0/3.0 , 2.0/3.0 , 1 ]
				  ,  [ 0 ,    0    , 1.0/3.0 , 1 ]
				  ,  [ 0 ,    0    ,    0    , 1 ] ] ) 
	def __init__( self ) :
		self.bz = Bezier()

		Points.__init__( self , self.bz )

		self.bz.set_visibility( Curve.POINTS  , False  )
		self.bz.set_visibility( Curve.CURVE   , True  )
		self.bz.set_visibility( Curve.POLYGON , False )

		self.bezier = []
		self.powerx = []
		self.powery = []
		self.powerz = []

		self.ptsx = []
		self.ptsy = []
		self.ptsz = []

		self.set_data( self.bezier )

		self.pow2bern() 

	def new( self , pos , data = None ) :
		Points.new( self , pos , data )

		self.update_matrix()
		self.update_polynomianls() 

	def move_current( self , v ) :
		Points.move_current( self , v )

		self.update_polynomianls()

	def delete( self , pos , dist = .05 ) :
		Points.delete( self , pos ,dist )

		self.update_matrix()
		self.update_polynomianls()

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BEZIER :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys  )

	def update_matrix( self ) :
		if len(self) < 2 : return

		self.matrix = self.quad2bound( self.mkmatrix(len(self)), self.num2size(len(self)), 3, 3 )

	def update_polynomianls( self ) :
		if len(self) < 2 : return

		self.ptsx = [ p[0] for p in self ]
		self.ptsy = [ p[1] for p in self ]
		self.ptsz = [ p[2] for p in self ]

		vx = self.mkvalues( self.ptsx , len(self) )
		vy = self.mkvalues( self.ptsy , len(self) )
		vz = self.mkvalues( self.ptsz , len(self) )

 		self.powerx[:] = sla.solve_banded( (3,3) , self.matrix , vx )
 		self.powery[:] = sla.solve_banded( (3,3) , self.matrix , vy )
 		self.powerz[:] = sla.solve_banded( (3,3) , self.matrix , vz )

		for i in reversed(range(len(self)-1)) :
			self.powerx.insert( i*3+3 , self.ptsx[i] )
			self.powery.insert( i*3+3 , self.ptsy[i] )
			self.powerz.insert( i*3+3 , self.ptsz[i] )

		self.pow2bern()

	def num2size( self , num ) :
		return (num-1)*(4-1)

	def mkvalues( self , v , num ) :
		if num < 2 : raise ValueError('Minimum interpolation points number is 2')

		size = self.num2size( num )
		b = np.zeros( size )

		k = 0
		for i in range(3,size-2,3) :
			b[i] = v[k+1] - v[k]
			k   += 1
		b[-2] = v[-1] - v[-2]

		return b

	def quad2bound( self , m , size , l , u ) :
		''' convert bound matrix from normal to bound representation '''
		mb = np.zeros( (l+u+1,size) )
		for i in xrange(size) :
			for j in xrange(size) :
				if u+i-j >= l+u+1 or u+i-j < 0 : continue
				mb[ u + i - j , j ] = m[ i , j ]
		return mb

	def mkmatrix( self , num ) :
		''' Calculates band matrix to solve C2 polynomial interpolation with 
		    second derivatives equal 0 on bounds. Polynomial on every interval
			is parametrized from 0 to 1.
		'''
		if num < 2 : raise ValueError('Minimum interpolation points number is 2')

		size = self.num2size( num )

		rows = []
		# boundary derivative
		rows.append( np.array( [ 0 , 2 ] , dtype=np.float32 ) )
		rows[-1].resize( size )

		for i in range(num-2) :
			# second derivatives
			rows.append( np.array( [0,0,0]*i + [6,2,0,0,-2] , dtype=np.float32 ) )
			rows[-1].resize( size )
			# first derivatives
			rows.append( np.array( [0,0,0]*i + [3,2,1,0,0,-1] , dtype=np.float32 ) )
			rows[-1].resize( size )
			# values
			rows.append( np.array( [0,0,0]*i + [1,1,1,0, 0] , dtype=np.float32 ) )
			rows[-1].resize( size )

		# boundary value
		rows.append( np.array( [0,0,0]*(num-2) + [1,1,1] , dtype=np.float32 ) )
		rows[-1].resize( size )
		# boundary derivative
		rows.append( np.array( [0,0,0]*(num-2) + [6,2,0] , dtype=np.float32 ) )
		rows[-1].resize( size )

		return np.array( rows )

	def pow2bern( self ) :
		del self.bezier[:]
		for i in range(0,len(self.powerx),4) :
			x = np.dot( self.Mpb , np.array( self.powerx[i:i+4] ) )
			y = np.dot( self.Mpb , np.array( self.powery[i:i+4] ) )
			z = np.dot( self.Mpb , np.array( self.powerz[i:i+4] ) )

			for j in reversed(range(4)) :
				if j == 3 and i != 0 : continue
				self.bezier.append( np.array([x[j],y[j],z[j],1]) )

