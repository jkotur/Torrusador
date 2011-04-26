
import numpy as np

from look.node import Node
from geom.point import Point

from points import Points

from geom.bezier import Bezier
from geom.curve import Curve
from geom.multi import MultiGeom

from copy import copy

def decasteljau( pts , t ) :
        if len(pts) <= 0 :
                return 0

        for k in reversed(range(0,len(pts))) :
                for i in xrange(0,k) :
                        pts[i] = pts[i]*(1.0-t) + pts[i+1]*t
        return pts[0]

class SurfaceC0( Points ) :
	def __init__( self , pts_vis = True , curve_vis = True , polygon_vis = False ) :
		self.size = ( 1 , 1 )
		self.dens = ( 1 , 1 )

		self.calc_size()
		self.allocate()

		mg = MultiGeom( (Bezier( 1 ) , Bezier( 1 ) ) )

		self.pts = []

		Points.__init__( self , mg )

		mg.set_visibility( Bezier.POINTS  , pts_vis     )
		mg.set_visibility( Bezier.CURVE   , False )
		mg.set_visibility( Bezier.POLYGON , False )

		self.set_data( (self.bezx,self.bezy) )

	def set_visibility( self , type , pts , curves , polys ) :
		if type == Curve.BEZIER :
			self.get_geom().set_visibility( Curve.POINTS  , pts    )
			self.get_geom().set_visibility( Curve.CURVE   , curves )
			self.get_geom().set_visibility( Curve.POLYGON , polys  )

	def calc_size( self ) :
		self.sizex = (self.size[0]*self.dens[0]*3+1 , self.size[1]*3+1)
		self.sizey = (self.size[1]*self.dens[1]*3+1 , self.size[0]*3+1)

	def allocate( self ) :
#        self.bezx = [np.array(np.zeros(3))]*self.sizex[0]*self.sizex[1]
#        self.bezy = [np.array(np.zeros(3))]*self.sizey[0]*self.sizey[1]
		self.bezx = [np.array(np.zeros(3))]*16*self.size[0]*self.size[1]
		self.bezy = [np.array(np.zeros(3))]*16*self.size[0]*self.size[1]


	def set_density( self , dens ) :
		self.dens = dens 
		self.calc_size()
		self.bezx , self.bezy = self.generate( self.pts , self.bezx , self.bezy , self.sizex , self.sizey , self.dens )

	def new( self , pos , which ) :
		if len(self) >= 3 : return

		Points.new( self , pos )

		if len(self) < 3 : return

		corners = []
		for p in self :
			corners.append( np.array(( p[0] , p[1] , p[2] )) )
		del self[:]

		corners.append( corners[2] + corners[0] - corners[1] )

		dx = (corners[1] - corners[0]) / (self.size[0]*3)
		dy = (corners[3] - corners[0]) / (self.size[1]*3)

		self.pts = []

		for xi in range(self.size[0]) :
			for yi in range(self.size[1]) :
				for x in range(4) :
					for y in range(4) :
						pt = corners[0] + dx * (x + xi * 3) + dy * (y+yi*3) 
						self.pts.append( pt )

		self.bezx , self.bezy = self.generate( self.pts , self.bezx , self.bezy , self.sizex , self.sizey , self.dens )

		self.get_geom().set_visibility( Bezier.CURVE , True )

	def generate( self , pts , bezx , bezy , sx , sy , dens ) :
		tmp = np.empty( 4 ) 
		for i in range(self.size[0]*self.size[1]) :
			for x in range(4) :
				id = i*16+x*4
				tmp = pts[id:id+4]
				bezx[id  ] = tmp[0]
				bezx[id+1] = decasteljau( copy(tmp) , 0.333 )
				bezx[id+2] = decasteljau( copy(tmp) , 0.666 )
				bezx[id+3] = tmp[3]
#                j = 0
#                for t in np.linspace(0,1,4) :
#                    bezx[id+j] = decasteljau( copy(tmp) , t )
#                    j+=1

		for i in range(self.size[0]*self.size[1]) :
			for y in range(4) :
				id = i*16+y*4
				for x in range(4) :
					tmp[x] = bezx[y+x*4+i*16]
				bezy[id  ] = tmp[0]
				bezy[id+1] = decasteljau( copy(tmp) , 0.333 )
				bezy[id+2] = decasteljau( copy(tmp) , 0.666 )
				bezy[id+3] = tmp[3]
#                j = 0 
#                for t in np.linspace(0,1,4) :
#                    bezy[id+j] = decasteljau( copy(tmp) , t )
#                    j+=1

		for i in range(self.size[0]*self.size[1]) :
			for x in range(4) :
				id = i*16+x*4
				for y in range(4) :
					tmp[y] = bezy[x+y*4+i*16]
				j = 0
				for t in np.linspace(0,1,4) :
					bezx[id+j] = decasteljau( copy(tmp) , t )
					j+=1

		return bezx , bezy

	def move_current( self , v ) :
		if self.current == None :
			return

		self.current += v

		self.bezx , self.bezy = self.generate( self.pts , self.bezx , self.bezy , self.sizex , self.sizey , self.dens )

	def bezx_to_bezy( self ) :
		for i in range(self.size[0]*self.size[1]) :
			for y in range(4) :
				for x in range(4) :
					self.bezy[x+y*4+i*16] = self.bezx[y+x*4+i*16]

	def find_nearest( self , pos , mindist = .05 ) :
		return self._find_nearest( pos , self.pts , mindist )


#        self.pts += pos

#    def delete( self , pos , dist = .05 ) :
#        return

#    def find_nearest( self , pos , mindist = .05 ) :
#        return self._find_nearest( pos , self.pts , mindist )

