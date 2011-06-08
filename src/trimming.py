
import math as m
import numpy as np

class TrimmingBorder :
	def __init__( self , minu , minv , maxu , maxv ) :
		self.minu = minu
		self.minv = minv
		self.maxu = maxu
		self.maxv = maxv

		self.offset = 0.0

		self.minuv =  minu + minv

	@property
	def min_u( self ) : return self.minu
	@property
	def min_v( self ) : return self.minv
	@property
	def max_u( self ) : return self.maxu
	@property
	def max_v( self ) : return self.maxv

	@property
	def beg_u( self ) : return self.min_u + self.offset
	@property
	def end_u( self ) : return float('inf')
	@property
	def beg_v( self ) : return self.min_v + self.offset
	@property
	def end_v( self ) : return float('inf')

	@property 
	def min_uv( self ) :
		return self.minuv

	@property
	def fake( self ) :
		return False

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

		self.minu = float('inf')
		self.minv = float('inf')
		self.maxu = float('-inf')
		self.maxv = float('-inf')

		self.endu = float('inf')
		self.endv = float('inf')
		
		self.loop = False
		self.oneborder = False

	@property
	def beg_u( self ) : return self.min_u
	@property
	def beg_v( self ) : return self.min_v

	@property
	def fake( self ) :
		i = 0
		if m.isinf(self.minu) : i+=1
		if m.isinf(self.maxu) : i+=1
		if m.isinf(self.minv) : i+=1
		if m.isinf(self.maxv) : i+=1
		return not self.loop and not self.oneborder and i>2

	@property
	def end_u( self ) : return self.endu
	@property
	def end_v( self ) : return self.endv

	def set_u_min( self , u ) :
		if not m.isinf(self.minu) : self.oneborder = True
		if u < self.minu :
			self.endu = self.minu
			self.minu = u
		else :
			self.endu = u

	def set_v_min( self , v ) :
		if not m.isinf(self.minv) : self.oneborder = True
		if v < self.minv :
			self.endv = self.minv
			self.minv = v
		else :
			self.endv = v

	def set_u_max( self , u ) :
		if not m.isinf(self.maxu) : self.oneborder = True
		if u > self.maxu : self.maxu = u

	def set_v_max( self , v ) :
		if not m.isinf(self.maxv) : self.oneborder = True
		if v > self.maxv : self.maxv = v

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
#            print self.a[i+bvi,1] , self.a[i+evi,1] , bnv , env
#            print self.a[i+bui,0] , self.a[i+eui,0] 
			du = ( self.a[i+bui,0] - self.a[i+eui,0] ) / float(env+1-bnv)
			bnu = int( m.ceil ( self.a[i+bui,0] / du ) )
			for i in range(env+1-bnv) :
				yield  (bnu+i)*du , (bnv+i)*dv

