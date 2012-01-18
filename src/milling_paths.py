import sys

import math as m
import numpy as np

import csurf

from look.node import Node

from geom.lines import Lines

from saver import save , save_commpressed

BLOCK_X = np.array((-1.5,1.9)) * 1.2
BLOCK_Y = np.array((-1.6,1.8)) * 1.2

FLAT_DRILL = 12.0
SMALL_DRILL = 8.0
HUGE_DRILL = 16.0

SCALE = 150.0 / float(BLOCK_X[1] - BLOCK_X[0])

BLOCK_H = -50.0 / SCALE
Z_ZERO = -10.0 / SCALE
MIN_INIT = 27 / SCALE
SAFE_POS = np.array((0,0,-150)) / SCALE

TRANS = np.array(( -0.2 , -0.1 , Z_ZERO ))

class Miller( Node ) :
	def __init__( self , curves ) :
		Node.__init__( self , Lines() , (1.0,0.5,0.0) )

		self.curves = curves
		self.paths = []

		self.init_r = HUGE_DRILL / 2.0 / SCALE
		self.flat_r = FLAT_DRILL / 2.0 / SCALE
		self.exac_r = SMALL_DRILL / 2.0 / SCALE 

		print 'Init drill: ' ,self.init_r 
		print 'Flat drill: ' ,self.flat_r
		print 'Exact drill: ' ,self.exac_r

		self.gen_paths()

		proc = lambda p : (p + TRANS)*SCALE + np.array((0,0, -SMALL_DRILL))

		save(0,'01_init.k16'   , self.paths , pre = proc )
		save(1,'02_border.f12' , self.paths , pre = proc )
		save(2,'03_flat.f12'   , self.paths , pre = proc )
		save(3,'04_exact.k8'   , self.paths , pre = proc )

		save_commpressed(0,'11_init_small.k16'   ,  self.paths ,pre = proc )
		save_commpressed(1,'12_border_small.f12' ,  self.paths ,pre = proc )
		save_commpressed(2,'13_flat_small.f12'   ,  self.paths ,pre = proc )
		save_commpressed(3,'14_exact_small.k8'   ,  self.paths ,pre = proc )

		self.set_data( self.paths )

		np.set_printoptions(suppress=True)


	def safe_goto( self , b , x , y , z ) :
		e = np.array((x , y , z))
		return np.array( [ np.array((b[0],b[1],BLOCK_H)) , SAFE_POS , np.array((e[0],e[1],BLOCK_H)) , e ] )

	def gen_paths( self ) :
		self.gen_configuration()
		print "Generating trimming curve..."
		self.trm_exact = self.find_trimming( self.exac_r )
		print "Generating initial path..."
		init_z0 = -self.init_r+self.exac_r
		init_path = self.gen_initial( self.init_r * 1.2 , self.init_r * 1.1 , BLOCK_H / 2.5 )
		print "Generating border path..."
		flat_z0 = self.exac_r
		flat_border = self.gen_border( self.flat_r * 1.02  , flat_z0, *self.trm_exact )
		self.remove_self_cuts( flat_border )
		print "Generating paths for flat surface..."
		flat_path = self.gen_flat( flat_z0, 128, 128, flat_border )
		print "Generating exact path..."
		exact_path = np.empty(0)
		exact_path = self.gen_exact( 0 , *self.trm_exact )
		print "All paths generated"

		flat_border = np.concatenate((self.safe_goto( init_path[-1] , BLOCK_X[0]-.3, BLOCK_Y[1], flat_border[0][2] ),flat_border))
		flat_border = np.concatenate((flat_border,self.safe_goto( flat_border[-1], BLOCK_X[1]+0.3, BLOCK_Y[0], flat_path[0][2] )))
		flat_path = np.concatenate((flat_path,self.safe_goto( flat_path[-1] , BLOCK_X[1]+0.1, BLOCK_Y[0] , exact_path[0][2] )))
		exact_path = np.concatenate((exact_path,self.safe_goto( exact_path[-1] , BLOCK_X[1]+0.1, BLOCK_Y[0], 0 )))

		self.paths.append( init_path )
		self.paths.append( flat_border )
		self.paths.append( flat_path )
		self.paths.append( exact_path )

#        self.paths.append( np.array(init_border))
		self.paths.append( np.array(((BLOCK_X[0],BLOCK_Y[0],Z_ZERO),(BLOCK_X[1],BLOCK_Y[0],Z_ZERO),(BLOCK_X[1],BLOCK_Y[1],Z_ZERO),(BLOCK_X[0],BLOCK_Y[1],Z_ZERO),(BLOCK_X[0],BLOCK_Y[0],Z_ZERO))) * np.array((1.2,1.2,1)) )

	def gen_configuration( self ) :
		self.head = self.curves.getat(0)
		self.hand = self.curves.getat(1)

		self.trm_uv_head = self.head.trimms[1]
		self.trm_uv_hand = self.hand.trimms[1]

	def get_curve_data( self , curve ) :
		return curve.size[0] , curve.size[1] , curve.array_pts

	def gen_initial( self , r , l , z ) :
		u , v , head_pts = self.get_curve_data( self.head )

		bu , eu = 7.0 , 12.0
		bv , ev = 0 , v

		pmin = csurf.bspline_surf( bu , 0 , head_pts )
		pmax = csurf.bspline_surf( bu , v , head_pts )

		if pmin[0] > pmax[0] :
			pmin , pmax = pmax , pmin
			bv   , ev   = ev   , bv

		bx , ex = BLOCK_X
		by , ey = BLOCK_Y

		path = []

		x = bx

		while x < ex :
			if x >= pmin[0] - r : break
			path.append( np.array((x,by,z)) )
			path.append( np.array((x,ey,z)) )
			x += r
			if x >= pmin[0] - r : break
			path.append( np.array((x,ey,z)) )
			path.append( np.array((x,by,z)) )
			x += r

		p = csurf.bspline_surf( bu , bv , head_pts )

		path[-2][0] = p[0] - self.init_r
		path[-1][0] = p[0] - self.init_r

		op = p = path[-1]

		nu = 64
		nv = 128
		iv = (ev-bv) / float(nv)
		v = bv
		s = m.copysign( 1 , ev - bv )

		while True :
			while s*v <= s*ev and p != None and m.fabs( p[0] - op[0] ) < l :
				p = csurf.bspline_surf( eu , v , head_pts )
				dv= csurf.bspline_surf_prime_v( eu , v , head_pts )
				du= csurf.bspline_surf_prime_u( eu , v , head_pts )
				n = np.cross( du , dv )
				n = n / np.linalg.norm( n )
				p = p + n * r
				v += iv
			op = p

			if s*v > s*ev : break


			if v < 12 and v > 5 :
				u1 = 8.0
				u2 = 11.0
			else :
				u1 = bu
				u2 = eu

			tp = []
			self.gen_line_u( head_pts , tp , r , v , u2 , u1 , nu )
			tp.insert( 0 , np.array((tp[0][0],by,tp[0][2])) )
			tp.append( np.array((tp[-1][0],ey,tp[-1][2])) )
			path += tp

			while s*v <= s*ev and p != None and m.fabs( p[0] - op[0] ) < l :
				p = csurf.bspline_surf( bu , v , head_pts )
				dv= csurf.bspline_surf_prime_v( bu , v , head_pts )
				du= csurf.bspline_surf_prime_u( bu , v , head_pts )
				n = np.cross( du , dv )
				n = n / np.linalg.norm( n )
				p = p + n * r
				v += iv
			op = p

			if s*v > s*ev : break

			if v < 12 and v > 5 :
				u1 = 8.0
				u2 = 11.0
			else :
				u1 = bu
				u2 = eu

			tp = []
			self.gen_line_u( head_pts , tp , r , v , u1 , u2 , nu )
			tp.insert( 0 , np.array((tp[0][0],ey,tp[0][2])) )
			tp.append( np.array((tp[-1][0],by,tp[-1][2])) )
			path += tp

		x = path[-1][0] + r

		while x < ex :
			path.append( np.array((x,ey,z)) )
			path.append( np.array((x,by,z)) )
			x += r 
			path.append( np.array((x,by,z)) )
			path.append( np.array((x,ey,z)) )
			x += r

		# move from center to bottom
		for i in range(len(path)) : path[i][2] += self.init_r

		return np.array( path )

	def gen_flat( self , z , nx , ny , border ) :
		bx , ex = BLOCK_X
		by , ey = BLOCK_Y

		a = self.gen_zigzag( bx , ex , by , ey , z , nx , ny , border ) 
		border = np.roll( border , -50 , 0 )
		ey = ey / 1.2
		b = self.safe_goto( a[-1], bx*1.1, ey, z )
		c = self.gen_zigzag( ex , bx , ey , by , z , nx , ny , border )

		return np.concatenate(( a , b , c ))

	def gen_zigzag( self , bx , ex , by , ey , z , nx , ny , border ) :
		path = []

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

		s = m.copysign( 1 , ey - by )
		y = by
		while s*y <= s*ey :
			cut = []
			for i in range(len(border)) :
				if within( y , border[i][1] , border[(i+1)%len(border)][1] ) :
					cut.append(i)

			sc = m.copysign( 1 , bx - ex )
			cut = sorted( cut , key = lambda i : sc * border[i][0] )

			if len(cut) :
				prev = cut[0]
				p0 = border[cut[0]  ]
				p1 = border[(cut[0]+1)%len(border)]
				tx = self.lerp( y , p0[1] , p1[1] , p0[0] , p1[0] )
			else :
				prev = None
				tx = bx

			path.append( np.array((ex,y,z)) )
			path.append( np.array((tx,y,z)) )
			y += dy

			cut = []
			for i in range(len(border)) :
				if within( y , border[i][1] , border[(i+1)%len(border)][1] ) :
					cut.append(i)

			sc = m.copysign( 1 , bx - ex )
			cut = sorted( cut , key = lambda i : sc * border[i][0] )

			if len(cut) :
				next = cut[0]
				p0 = border[cut[0]  ]
				p1 = border[(cut[0]+1)%len(border)]
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
					if s * (y-1.7*dy) <= s * border[i][1] :
						path.append( border[i] )

			path.append( np.array((tx,y,z)) )
			path.append( np.array((ex,y,z)) )

			y += dy

		return np.array(path)

	def gen_flat_old( self , z , nx , ny , border ) :
		path = []

		bx , ex = BLOCK_X
		by , ey = BLOCK_Y

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

			sc = m.copysign( 1 , ex - bx )
			cut = sorted( cut , key = lambda i : sc * border[i][0] )

			path.append( np.array((bx,y,z)) )
			
			for i in range(0,len(cut),2) :
				p0 = border[cut[i]  ]
				p1 = border[cut[i]+1]
				tx = self.lerp( y , p0[1] , p1[1] , p0[0] , p1[0] )

				path.append( np.array((tx,y,z)) )
				path.append( np.array((tx,y,BLOCK_H)) )

				i+=1

				p0 = border[cut[i]  ]
				p1 = border[cut[i]+1]
				tx = self.lerp( y , p0[1] , p1[1] , p0[0] , p1[0] )

				path.append( np.array((tx,y,BLOCK_H)) )
				path.append( np.array((tx,y,z)) )


			path.append( np.array((ex,y,z)) )

			bx , ex = ex , bx
			y += dy

		return np.array(path)

	def gen_bspline_point( self , u , v , r , pts ) :
		p = csurf.bspline_surf        ( u , v , pts )
		dv= csurf.bspline_surf_prime_v( u , v , pts )
		du= csurf.bspline_surf_prime_u( u , v , pts )
		n = np.cross( du , dv )
		n = n / np.linalg.norm( n )
		return p + n * r

	def gen_border( self , r , z0 , trm , tdhead , tdhand ) :
		path = []
		uhead , vhead , phead = self.get_curve_data( self.head )
		uhand , vhand , phand = self.get_curve_data( self.hand )

		nv = 128

		path.append( csurf.bspline_surf( 6.0, vhead , phead ) + np.array((-r,0,0)))

		for iv in np.linspace(vhead,0,nv) :
			path.append( self.gen_bspline_point( 6.0 , iv , r , phead ) )

		path.append( csurf.bspline_surf( 6.0, 0 , phead ) + np.array((r,0,0)))
		path.append( csurf.bspline_surf(13.0, 0 , phead ) + np.array((r,0,0)))

		for iv in np.linspace(0,vhead,nv) :
			p = self.gen_bspline_point( 13.0 , iv , r , phead )
			if self.check_pass( p , trm[-1] , tdhead[-1][1] ) :
#                path.append( trm[-1] )
				break
			path.append( p )

		for iv in np.linspace(vhand,0,nv) :
			p = self.gen_bspline_point( 3.0 , iv , r , phand )
			if self.check_pass( p , trm[-1] , tdhand[-1][1] ) :
				continue
			path.append( np.array( p ) )

		path.append( csurf.bspline_surf( 3.0, 0 , phand ) + np.array((0,-r,0)))
		path.append( csurf.bspline_surf( 7.0, 0 , phand ) + np.array((0,-r,0)))

		for iv in np.linspace(0,vhand,nv) :
			p = self.gen_bspline_point( 7.0 , iv , r , phand )
			if self.check_pass( p , trm[0] , tdhand[0][1] ) :
#                path.append( trm[0] )
				break
			path.append( p )

		for iv in np.linspace(0,vhead,nv) :
			p = self.gen_bspline_point( 13.0 , iv , r , phead )
			if not self.check_pass( p , trm[0] , tdhead[0][1] ) :
				continue
			path.append( p )

		path.append( csurf.bspline_surf(13.0, vhead , phead ) + np.array((-r,0,0)))

		path.append( path[0] )

		for v in path : v[2] = z0

		return path

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
	def find_trimming( self , r ) :
		u , v , head_pts = self.get_curve_data( self.head )
		u , v , hand_pts = self.get_curve_data( self.hand )

		head_trm = self.trm_uv_head
		hand_trm = self.trm_uv_hand

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

			ln = m.sqrt(2) * r / m.sqrt( 1 + np.dot( head_n , hand_n ) ) * 1.08

			path.append( p + n * ln )


			fi += di

		return path , head_derv , hand_derv

	def gen_exact( self , z0 , trm , tdhead , tdhand ) :
		path_hand = []
		path_head = []

		#
		# hand
		#
		u , v , hand_pts = self.get_curve_data( self.hand )

		tn = np.cross( trm[-1] - trm[0] , np.array((0,0,1)) )
		tp = trm[0]

		bu = 3.0
		eu = 7.0
		nu = 64
		nv = 128
		dv = v / float(nv)
		iv = 0.0
		ev = iv

		while iv <= v :
			p = csurf.bspline_surf( eu , iv , hand_pts )
			if self.check_pass( p , tp , tn ) :
				self.gen_line_u_with_trimming( iv , bu , eu , nu , z0 , hand_pts , trm , tdhand , path_hand )
				ev = iv
			iv += dv
			p = csurf.bspline_surf( eu , iv , hand_pts )
			if self.check_pass( p , tp , tn ) :
				self.gen_line_u_with_trimming( iv , eu , bu , nu , z0 , hand_pts , trm , tdhand , path_hand )
				ev = iv
			iv += dv

		trmuv = self.trm_uv_hand.l
		i = 1
		for a in np.linspace(0,1,5) :
			for uv in trmuv if not i%2 else reversed(trmuv) :
				if uv[0] > 3.0 and uv[0] < 7.0 :
					v = a*(uv[1] - 0.7) + (1-a)*ev
					p = csurf.bspline_surf        ( uv[0] , v , hand_pts )
					dv= csurf.bspline_surf_prime_v( uv[0] , v , hand_pts )
					du= csurf.bspline_surf_prime_u( uv[0] , v , hand_pts )

					n = np.cross( du , dv )
					n = n / np.linalg.norm( n )

					path_hand.append( np.array( p + n * self.exac_r ) )
			i += 1

		path_hand += trm

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
			self.gen_line_u_with_trimming( iv , bu , eu , nu , z0 , head_pts , trm , tdhead , path_head )

			iv += dv

			self.gen_line_u_with_trimming( iv , eu , bu , nu , z0 , head_pts , trm , tdhead , path_head )

			iv += dv

		print 

		path = path_hand

		path.append( path_hand[-1] + np.array((0,0,-1.2)) )
		path.append( path_head[ 1] + np.array((0,0,-1.2)) )

		path += path_head

		# move from center to bottom
		for i in range(len(path)) : path[i][2] += self.exac_r

		return np.array( path )

	def gen_line_u( self , pts , path , r , v , bu , eu , nu ) :
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
					path.append( np.array( p + tn*r ) )
				else : # normal is well defined
					pn = cn
					cn = n
					path.append( np.array( p + cn * r ) )
			else : # normal is undefined
				cn = None

			odu = ndu

	def gen_line_u_with_trimming( self , v , bu , eu , nu , z0 , pts , trm , dtrm , path ) :
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
			while ri>=0 and self.check_pass( p , trm[ri] , dtrm[ri][1] ) :
				ri-=1

#            if( fi<len(trm) and self.check_pass( p, trm[fi], dtrm[fi][0] )) \
#            and( ri>=0       and not self.check_pass( p, trm[ri], dtrm[ri][0] )) :
			if( fi<len(trm) and ri>=0 ) and \
			  ((self.check_pass( p, trm[fi], dtrm[fi][0] )) or \
			  ( self.check_pass( p, trm[ri], dtrm[ri][0] ))) :
				continue

#            if ri == -1 and fi == 0 : continue

#            if not self.check_pass( p , np.array((0,0,z0)) , np.array((0,0,-1)) ) :
#                continue

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

	def remove_self_cuts( self , l ) :
		def ccw( a , b , c ) :
			return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])

		def nx( x1 , x2 , x3 , x4 , y1 , y2 , y3 , y4 ) :
			return ((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4)) / \
			             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))
		def ny( x1 , x2 , x3 , x4 , y1 , y2 , y3 , y4 ) :
			return ((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4)) / \
			             ((x1-x2)*(y3-y4)-(y1-y2)*(x3-x4))

		i = 0
		while i < len(l)-1 :
			j = i+1
			while j < len(l)-1 :
				a0 = l[i  ]
				a1 = l[i+1]
				b0 = l[j  ]
				b1 = l[j+1]

				if ccw( a0 , b0 , b1 ) != ccw(a1,b0,b1) and \
				   ccw( a0 , a1 , b0 ) != ccw(a0,a1,b1) :
					x = nx( a0[0] , a1[0] , b0[0] , b1[0] , a0[1] , a1[1] , b0[1] , b1[1] )
					y = ny( a0[0] , a1[0] , b0[0] , b1[0] , a0[1] , a1[1] , b0[1] , b1[1] )
					l[j+1][0] = x
					l[j+1][1] = y
					del l[i+1:j+1]
					j = i+1
				j+=1
			i+=1


