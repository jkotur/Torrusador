
import numpy as np

import csurf

class Cutter :
	def __init__( self ) :
		self.tocut = []

	def clear( self ) :
		self.tocut = []

	def add( self , surf ) :
		if surf not in self.tocut :
			if len(self.tocut) >= 2 :
				self.tocut.pop(0)
			self.tocut.append(surf)

	def cuts( self , surf ) :
		return surf in self.tocut

	def reset_trimms( self ) :
		for s in self.tocut : s.reset_trimms()

	def reset_ind( self ) :
		for s in self.tocut : s.gen_ind()


	def cut( self , pos , delta ) :
		if len(self.tocut) < 2 :
			return (None,None)

		u1 = self.tocut[0].size[0] / 2.0
		v1 = self.tocut[0].size[1] / 2.0
		u2 = self.tocut[1].size[0] / 2.0
		v2 = self.tocut[1].size[1] / 2.0

		uvuv = self.find_first_uv( np.array((u1,v1,u2,v2)) )

		self.find_trimming( uvuv , delta )

		return (3,5)

	def find_first_uv( self , uvuv ) :
		uvuv = csurf.cut_bsplines(
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() , uvuv )

		self.tocut[0].trim_p0 = csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts )
		self.tocut[1].trim_p0 = csurf.bspline_surf( uvuv[2], uvuv[3], self.tocut[1].array_pts )

		print uvuv[:2] , self.tocut[0].trim_p0
		print uvuv[2:] , self.tocut[1].trim_p0

		return uvuv

	def find_trimming( self , uvuv , delta ) :
		maxuvuv = np.array((self.tocut[0].size[0],self.tocut[0].size[1],self.tocut[1].size[0],self.tocut[1].size[1]))

		baseuvuv = uvuv

		self.tocut[0].begin_trimming_curve()
		self.tocut[1].begin_trimming_curve()

		self.tocut[0].append_trimming_uv( uvuv[0] , uvuv[1] )
		self.tocut[1].append_trimming_uv( uvuv[2] , uvuv[3] )

		trimming = [ csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) ]
		self.tocut[0].trimming_curve = trimming
		while all( uvuv < maxuvuv ) and all( uvuv > np.zeros(4) ) :
			print 'Newton     (' , uvuv , ')' , '(' , maxuvuv , ')'
			uvuv = csurf.next_cut_bsplines( 
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() ,
				uvuv , trimming[-1] , delta )
			self.tocut[0].append_trimming_uv( uvuv[0] , uvuv[1] )
			self.tocut[1].append_trimming_uv( uvuv[2] , uvuv[3] )

			trimming.append( csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) )

		self._add_minmax( uvuv , maxuvuv )

		uvuv = baseuvuv
		while all( uvuv < maxuvuv ) and all( uvuv > np.zeros(4) ) :
			print 'Newton rev (' , uvuv , ')' , '(' , maxuvuv , ')'
			uvuv = csurf.next_cut_bsplines( 
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() ,
				uvuv , trimming[0] , delta , inv = True )
			self.tocut[0].prepend_trimming_uv( uvuv[0] , uvuv[1] )
			self.tocut[1].prepend_trimming_uv( uvuv[2] , uvuv[3] )

			trimming.insert( 0 , csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) )

		self._add_minmax( uvuv , maxuvuv )

		self.tocut[0].end_trimming()
		self.tocut[1].end_trimming()

	def _add_minmax( self , uvuv , maxuvuv ) :
		if uvuv[0] <= 0          : self.tocut[0].add_v_min( uvuv[1] )
		if uvuv[1] <= 0          : self.tocut[0].add_u_min( uvuv[0] )
		if uvuv[2] <= 0          : self.tocut[1].add_v_min( uvuv[3] )
		if uvuv[3] <= 0          : self.tocut[1].add_u_min( uvuv[2] )
		if uvuv[0] >= maxuvuv[0] : self.tocut[0].add_v_max( uvuv[1] )
		if uvuv[1] >= maxuvuv[1] : self.tocut[0].add_u_max( uvuv[0] )
		if uvuv[2] >= maxuvuv[2] : self.tocut[1].add_v_max( uvuv[3] )
		if uvuv[3] >= maxuvuv[3] : self.tocut[1].add_u_max( uvuv[2] )

