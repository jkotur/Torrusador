
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

	def cut( self ) :
		if len(self.tocut) < 2 :
			return (None,None)

		uvuv = self.find_first_uv()

		self.find_trimming( uvuv )

		return (3,5)

	def find_first_uv( self ) :
		u1 = self.tocut[0].size[0] / 2.0
		v1 = self.tocut[0].size[1] / 2.0
		u2 = self.tocut[1].size[0] / 2.0
		v2 = self.tocut[1].size[1] / 2.0
		uvuv = csurf.cut_bsplines(
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() , np.array((u1,v1,u2,v2)) )

		self.tocut[0].trim_p0 = csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts )
		self.tocut[1].trim_p0 = csurf.bspline_surf( uvuv[2], uvuv[3], self.tocut[1].array_pts )

		print self.tocut[0].trim_p0
		print self.tocut[1].trim_p0

		return uvuv

	def find_trimming( self , uvuv ) :
		maxuvuv = np.array((self.tocut[0].size[0],self.tocut[0].size[1],self.tocut[1].size[0],self.tocut[1].size[1]))

		baseuvuv = uvuv

		trimming = [ csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) ]
		self.tocut[0].trimming_curve = trimming
		while all( uvuv < maxuvuv ) and all( uvuv > np.array((1,1,1,1)) ) :
			print 'Newton (' , uvuv , ')' , '(' , maxuvuv , ')'
			uvuv = csurf.next_cut_bsplines( 
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() ,
				uvuv , trimming[-1] , 0.01 )
			trimming.append( csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) )
		uvuv = baseuvuv
		while all( uvuv < maxuvuv ) and all( uvuv > np.array((1,1,1,1)) ) :
			print 'Newton (' , uvuv , ')' , '(' , maxuvuv , ')'
			uvuv = csurf.next_cut_bsplines( 
				self.tocut[0].get_array_pts() ,
				self.tocut[1].get_array_pts() ,
				uvuv , trimming[-1] , 0.01 , inv = True )
			trimming.append( csurf.bspline_surf( uvuv[0], uvuv[1], self.tocut[0].array_pts ) )
		print trimming

