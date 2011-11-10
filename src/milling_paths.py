import sys

import math as m
import numpy as np

import csurf

from look.node import Node

from geom.lines import Lines

class Miller( Node ) :
	def __init__( self , curves ) :
		Node.__init__( self , Lines() , (1.0,0.5,0.0) )

		self.curves = curves
		self.paths = []

		self.init_r = 0.08
		self.flat_r = 0.05
		self.exac_r = 0.04

		self.gen_paths()

		print len(self.paths)
		self.save(0,'border.f10')
		self.save(1,'exact.k8')

		self.set_data( self.paths )

		np.set_printoptions(suppress=True)

	def save( self , num , filename ) :
		with open(filename,'w+') as f :
			i = 0
			for p in self.paths[num] :
				p = p*100
				f.write( 'N%dG01X%fY%fZ%f\n' % ( i , p[0] , p[1] ,-p[2] ) )
				i+=1

	def gen_paths( self ) :
		self.gen_configuration()
		print "Generating initial path..."
		self.gen_initial()
		print "Generating paths for flat surface path..."
		self.gen_flat()
		print "Generating border path..."
		self.gen_border()
		print "Generating exact path..."
		self.gen_exact()
		print "All paths generated"

	def gen_configuration( self ) :
		pass

	def get_curve_data( self , curve ) :
		return curve.size[0] , curve.size[1] , curve.array_pts

	def gen_initial( self ) :
		pass

	def gen_flat( self ) :
		pass

	def gen_border( self ) :
		head = self.curves.getat(0)
		hand = self.curves.getat(1)

		path = []
		u , v , pts = self.get_curve_data( head )

		trimming = head.trimms[1]

		for iv in np.linspace(0,v,64) :
			if iv > trimming.minimal_v and iv < trimming.maximal_v :
				continue
			p = csurf.bspline_surf        ( 6.0, iv , pts )
			dv= csurf.bspline_surf_prime_v( 6.0, iv , pts )
			du= csurf.bspline_surf_prime_u( 6.0, iv , pts )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		for iv in np.linspace(v,0,64) :
			if iv > trimming.minimal_v and iv < trimming.maximal_v :
				continue
			p = csurf.bspline_surf        (13.0, iv , pts )
			dv= csurf.bspline_surf_prime_v(13.0, iv , pts )
			du= csurf.bspline_surf_prime_u(13.0, iv , pts )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		path.append( path[0] )

		self.paths.append( np.array( path ) )

	def gen_exact( self ) :
		head = self.curves.getat(0)
		hand = self.curves.getat(1)

		path = []
		u , v , pts = self.get_curve_data( head )

		trm = head.trimms[1]
		vid = trm.minimal_v_id

		bu = 6.0
		eu = 13.0
		nu = 64
		nv = 128
		dv = v / float(nv)
		iv = 0.0

		while iv <= v :
			while vid-2 >= 0 and trm.l[vid-1][1] < iv : vid-=1
			if iv < trm.l[vid-1][1] and iv > trm.l[vid][1] :
				teu = trm.l[vid-1][0]
			else :
				teu = eu

			self.gen_line_u( pts , path , iv , bu , teu , nu )

			iv += dv

			while vid-2 >= 0 and trm.l[vid-1][1] < iv : vid-=1
			if iv < trm.l[vid-1][1] and iv > trm.l[vid][1] :
				teu = trm.l[vid-1][0]
			else :
				teu = eu

			self.gen_line_u( pts , path , iv , teu , bu , nu )

			iv += dv

		path.append( path[-1] + np.array((-.2,0,0 )) )
		path.append( path[-1] + np.array((0,-3.5,0)) )
		path.append( path[-1] + np.array((2,0,0)) )

		u , v , pts = self.get_curve_data( hand )

		trm = hand.trimms[1]

		v = trm.minimal_v

		bu = 3.0
		eu = 7.0
		nu = 64
		nv = 128
		dv = v / float(nv)
		iv = 0.0


		while iv <= v :
			self.gen_line_u( pts , path , iv , bu , eu , nu )
			iv += dv
			self.gen_line_u( pts , path , iv , eu , bu , nu )
			iv += dv

		self.paths.append( np.array( path ) )

	def gen_line_u( self , pts , path , v , bu , eu , nu ) :
		odu = None
		cn = None # current normal
		pn = None # previous normal

		for iu in np.linspace(bu,eu,nu) :
			sys.stdout.write('.')

			uv = np.array((iu,v))

			p = csurf.bspline_surf        ( iu, v, pts )
			dv= csurf.bspline_surf_prime_v( iu, v, pts )
			du= csurf.bspline_surf_prime_u( iu, v, pts )
			n = np.cross( du , dv )
			nlen = np.linalg.norm( n )
			dlen = np.linalg.norm( du )
			ndu  = du / dlen
			# paths count optimization
			if odu != None and np.allclose(ndu,odu,atol=0.001) :
				continue
			if dlen > 0.01 :
				n = n / nlen
				if cn == None and pn != None : # C0 edge
					cn = n
					tn = (pn+cn)
					tn = tn / np.linalg.norm(tn)
					path.append( np.array( p + tn*self.exac_r ) )
				else : # normal is well defined
					pn = cn
					cn = n
					path.append( np.array( p + cn * self.exac_r ) )
			else : # normal is undefined
				cn = None

			odu = ndu
