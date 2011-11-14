import sys

import math as m
import numpy as np

import csurf

from look.node import Node

from geom.lines import Lines

BLOCK_X = (-2,2)
BLOCK_Y = (-2,2)
BLOCK_H = 2

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
		self.save(1,'flat.f10')
#        self.save(2,'exact.k8')

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
		print "Generating trimming curve..."
		self.find_trimming()
		print "Generating initial path..."
		self.gen_initial()
		print "Generating border path..."
		self.gen_border()
		print "Generating paths for flat surface path..."
		self.gen_flat()
#        print "Generating exact path..."
#        self.gen_exact()
		print "All paths generated"

	def gen_configuration( self ) :
		self.head = self.curves.getat(0)
		self.hand = self.curves.getat(1)

	def get_curve_data( self , curve ) :
		return curve.size[0] , curve.size[1] , curve.array_pts

	def gen_initial( self ) :
		pass

	def gen_flat( self ) :
		border = self.paths[-1]

		path = []

		bx = -2
		ex =  2
		nx = 128
		by = -2
		ey =  2
		ny = 128

		dy = 2.0*(ey-by)/float(ny)

		minyid = None
		maxyid = None
		for i in range(len(border)) :
			if minyid == None or border[i][1] < border[minyid][1] :
				minyid = i
			if maxyid == None or border[i][1] > border[maxyid][1] :
				maxyid = i

		def within( y , y0 , y1 ) :
			return (y>y0 and y<y1) or (y>y1 and y<y0)

		np.set_printoptions(suppress=True)

		y = by
		while y <= ey :
			cut = []
			for i in range(len(border)-1) :
				if within( y , border[i][1] , border[i+1][1] ) :
					cut.append(i)

			cut = sorted( cut , key = lambda i :-border[i][0] )

			np.set_printoptions(suppress=True)

			if len(cut) :
				prev = cut[0]
				p0 = border[cut[0]  ]
				p1 = border[cut[0]+1]
				tx = self.lerp( y , p0[1] , p1[1] , p0[0] , p1[0] )
			else :
				prev = None
				tx = bx

			path.append( np.array((ex,y,0)) )
			path.append( np.array((tx,y,0)) )
			y += dy

			cut = []
			for i in range(len(border)-1) :
				if within( y , border[i][1] , border[i+1][1] ) :
					cut.append(i)

			cut = sorted( cut , key = lambda i :-border[i][0] )

			if len(cut) :
				next = cut[0]
				p0 = border[cut[0]  ]
				p1 = border[cut[0]+1]
				tx = self.lerp( y , p0[1] , p1[1] , p0[0] , p1[0] ) 
			else :
				next = None
				tx = bx

			if not prev and next :
				prev = minyid
			if prev and not next :
				next = maxyid

			if prev and next :
				for i in range( prev , next , 1 if prev < next else -1 ) :
					path.append( border[i] )

			path.append( np.array((tx,y,0)) )
			path.append( np.array((ex,y,0)) )
			y += dy

		self.paths.append( np.array(path) )

	def gen_border( self ) :
		path = []
		uhead , vhead , phead = self.get_curve_data( self.head )
		uhand , vhand , phand = self.get_curve_data( self.hand )

		nv = 64

		path.append( csurf.bspline_surf( 6.0, vhead , phead ) + np.array((-self.flat_r,0,0)))

		for iv in np.linspace(vhead,0,nv) :
			p = csurf.bspline_surf        ( 6.0, iv , phead )
			dv= csurf.bspline_surf_prime_v( 6.0, iv , phead )
			du= csurf.bspline_surf_prime_u( 6.0, iv , phead )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		path.append( csurf.bspline_surf( 6.0, 0 , phead ) + np.array((self.flat_r,0,0)))
		path.append( csurf.bspline_surf(13.0, 0 , phead ) + np.array((self.flat_r,0,0)))

		for iv in np.linspace(0,vhead,nv) :
			p = csurf.bspline_surf        (13.0, iv , phead )

			if self.check_pass( p , self.trm[-1] , self.tdhead[-1][1] ) :
				break

			dv= csurf.bspline_surf_prime_v(13.0, iv , phead )
			du= csurf.bspline_surf_prime_u(13.0, iv , phead )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		for iv in np.linspace(vhand,0,nv) :
			p = csurf.bspline_surf        ( 3.0, iv , phand )

			if self.check_pass( p , self.trm[-1] , self.tdhand[-1][1] ) :
				continue

			dv= csurf.bspline_surf_prime_v( 3.0, iv , phand )
			du= csurf.bspline_surf_prime_u( 3.0, iv , phand )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		path.append( csurf.bspline_surf( 3.0, 0 , phand ) + np.array((0,-self.flat_r,0)))
		path.append( csurf.bspline_surf( 7.0, 0 , phand ) + np.array((0,-self.flat_r,0)))

		for iv in np.linspace(0,vhand,nv) :
			p = csurf.bspline_surf        ( 7.0, iv , phand )

			if self.check_pass( p , self.trm[0] , self.tdhand[0][1] ) :
				break

			dv= csurf.bspline_surf_prime_v( 7.0, iv , phand )
			du= csurf.bspline_surf_prime_u( 7.0, iv , phand )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		for iv in np.linspace(0,vhead,nv) :
			p = csurf.bspline_surf        (13.0, iv , phead )

			if not self.check_pass( p , self.trm[0] , self.tdhead[0][1] ) :
				continue

			dv= csurf.bspline_surf_prime_v(13.0, iv , phead )
			du= csurf.bspline_surf_prime_u(13.0, iv , phead )
			n = np.cross( du , dv )
			n = n / np.linalg.norm( n )
			path.append( np.array( p + n * self.flat_r ) )

		path.append( csurf.bspline_surf(13.0, vhead , phead ) + np.array((-self.flat_r,0,0)))

		path.append( path[0] )

		self.paths.append( np.array( path ) )

	def lerp( self , x , bx , ex , by , ey ) :
		return (x-bx) / (ex-bx) * (ey-by) + by 

	#
	# checking if p is below or above plane based on point p0 and normal n
	#
	def check_pass( self , p , p0 , n ) :
		return np.dot( p - p0 , n ) > 0 

	#
	# trimming curve in object space
	#
	def find_trimming( self ) :
		u , v , head_pts = self.get_curve_data( self.head )
		u , v , hand_pts = self.get_curve_data( self.hand )

		head_trm = self.head.trimms[1]
		hand_trm = self.hand.trimms[1]

		bi  = min( head_trm.minimal_v_id , head_trm.maximal_v_id )
		ei  = max( head_trm.minimal_v_id , head_trm.maximal_v_id )
		nv = 32
		di = (ei - bi) / float(nv)

		path = []
		head_derv = []
		hand_derv = []

		fi = float(bi)
		while fi <= ei :
			i = int(fi)
			p = csurf.bspline_surf( head_trm.l[i][0] , head_trm.l[i][1] , head_pts )

			du = csurf.bspline_surf_prime_u( hand_trm.l[i][0] , hand_trm.l[i][1] , hand_pts )
			dv = csurf.bspline_surf_prime_v( hand_trm.l[i][0] , hand_trm.l[i][1] , hand_pts )
			hand_n = np.cross( du , dv )
			hand_n = hand_n / np.linalg.norm( hand_n )

			hand_derv.append( (du,dv) )

			du = csurf.bspline_surf_prime_u( head_trm.l[i][0] , head_trm.l[i][1] , head_pts )
			dv = csurf.bspline_surf_prime_v( head_trm.l[i][0] , head_trm.l[i][1] , head_pts )
			head_n = np.cross( du , dv )
			head_n = head_n / np.linalg.norm( head_n )

			head_derv.append( (du,dv) )

			n = head_n + hand_n
			n = n / np.linalg.norm( n )

			ln = m.sqrt(2) * self.exac_r / m.sqrt( 1 + np.dot( head_n , hand_n ) )

			path.append( p + n * ln )


			fi += di

		self.trm    = path
		self.tdhead = head_derv
		self.tdhand = hand_derv

	def gen_exact( self ) :
		path = []

		#
		# head
		#
		u , v , head_pts = self.get_curve_data( self.head )

		bu = 6.0
		eu = 13.0
		nu = 64
		nv = 128
		dv = v / float(nv)
		iv = 0.0

		while iv <= v :
			self.gen_line_u_with_trimming( iv , bu , eu , nu , head_pts , self.trm , self.tdhead , path )

			iv += dv

			self.gen_line_u_with_trimming( iv , eu , bu , nu , head_pts , self.trm , self.tdhead , path )

			iv += dv

		path.append( path[-1] + np.array((-.2,0,0 )) )
		path.append( path[-1] + np.array((0,-3.5,0)) )
		path.append( path[-1] + np.array((2,0,0)) )

		u , v , hand_pts = self.get_curve_data( self.hand )

		#
		# hand
		#
		tn = np.cross( self.trm[-1] - self.trm[0] , np.array((0,0,1)) )
		tp = self.trm[0]

		bu = 3.0
		eu = 7.0
		nu = 64
		nv = 128
		dv = v / float(nv)
		iv = 0.0

		while iv <= v :
			p = csurf.bspline_surf( eu , iv , hand_pts )
			if self.check_pass( p , tp , tn ) :
				self.gen_line_u_with_trimming( iv , bu , eu , nu , hand_pts , self.trm , self.tdhand , path )
			iv += dv
			p = csurf.bspline_surf( eu , iv , hand_pts )
			if self.check_pass( p , tp , tn ) :
				self.gen_line_u_with_trimming( iv , eu , bu , nu , hand_pts , self.trm , self.tdhand , path )
			iv += dv

		path += reversed( self.trm )

		print 

		self.paths.append( np.array( path ) )

	def gen_line_u( self , pts , path , v , bu , eu , nu ) :
		sys.stdout.write('.')
		sys.stdout.flush()

		odu = None
		cn = None # current normal
		pn = None # previous normal

		for iu in np.linspace(bu,eu,nu) :

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

	def gen_line_u_with_trimming( self , v , bu , eu , nu , pts , trm , dtrm , path ) :
		sys.stdout.write('.')
		sys.stdout.flush()

		odu = None
		cn = None # current normal
		pn = None # previous normal

		for iu in np.linspace(bu,eu,nu) :

			p = csurf.bspline_surf        ( iu, v, pts )
			dv= csurf.bspline_surf_prime_v( iu, v, pts )
			du= csurf.bspline_surf_prime_u( iu, v, pts )

			fi = 0
			while fi<len(trm) and not self.check_pass( p , trm[fi] , dtrm[fi][1] ) :
				fi+=1
			ri = len(trm)-1
			while ri>=0 and not self.check_pass( p , trm[ri] , dtrm[ri][1] ) :
				ri-=1

			if( fi<len(trm) and self.check_pass( p, trm[fi], dtrm[fi][0] )) \
			or( ri>=0       and self.check_pass( p, trm[ri], dtrm[ri][0] )) :
				continue

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
