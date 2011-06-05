
import math as m
import numpy as np

class TrimmingBorder :
	def __init__( self , minu , minv , maxu , maxv ) :
		self.minu = minu
		self.minv = minv
		self.maxu = maxu
		self.maxv = maxv

		self.minuv =  minu + minv

	@property 
	def min_uv( self ) :
		return self.minuv

	def get_intersections_u( self , du ) :
		u = 0 
		while u <= self.maxu :
			yield u,self.minv
			u += du

	def get_intersections_v( self , dv ) :
		v = 0 
		while v <= self.maxv :
			yield self.minu,v
			v += dv

class TrimmingCurve( TrimmingBorder ) :
	def __init__( self ) :
		self.a = None
		self.l = None
		self.minuv = None

	def update_min( self , u , v ) :
		if self.minuv == None or u+v < self.minuv :
			self.minuv = u+v

	def start( self ) :
		self.l = []

	def add_back( self , u , v ) :
		self.l.append( np.array((u,v)) )
		self.update_min(u,v)

	def add_front( self , u , v ) :
		self.l.insert( 0 , np.array((u,v)) )
		self.update_min(u,v)

	def end( self ) :
		self.a = np.array( self.l )
		print self.a

	def get_intersections_u( self , du ) :
		for i in range(1,len(self.a)) :
			if self.a[i,0] - self.a[i-1,0] > 0 :
					bui , eui =  -1 ,  0
			else :	bui , eui =   0 , -1
			if self.a[i,1] - self.a[i-1,1] > 0 :
					bvi , evi =  -1 ,  0
			else :	bvi , evi =   0 , -1
			bnu = int( m.ceil ( self.a[i+bui,0] / du ) )
			enu = int( m.floor( self.a[i+eui,0] / du ) )
			dv = ( self.a[i+bvi,1] - self.a[i+evi,1] ) / float(enu+1-bnu)
			bnv = int( m.ceil ( self.a[i+bvi,1] / dv ) )
			for i in range(enu+1-bnu) :
				yield  (bnu+i)*du , (bnv+i)*dv

	def get_intersections_v( self , dv ) :
		for i in range(1,len(self.a)) :
			if self.a[i,1] - self.a[i-1,1] > 0 :
					bvi , evi =  -1 ,  0
			else :	bvi , evi =   0 , -1
			if self.a[i,0] - self.a[i-1,0] > 0 :
					bui , eui =  -1 ,  0
			else :	bui , eui =   0 , -1
			bnv = int( m.ceil ( self.a[i+bvi,1] / dv ) )
			env = int( m.floor( self.a[i+evi,1] / dv ) )
			print self.a[i+bvi,1] , self.a[i+evi,1] , bnv , env
			print self.a[i+bui,0] , self.a[i+eui,0] 
			du = ( self.a[i+bui,0] - self.a[i+eui,0] ) / float(env+1-bnv)
			bnu = int( m.ceil ( self.a[i+bui,0] / du ) )
			for i in range(env+1-bnv) :
				yield  (bnu+i)*du , (bnv+i)*dv

class TrimmingLoop( TrimmingCurve ) :
	pass

