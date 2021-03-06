# vim: set fileencoding=utf-8

import operator as op

import math as m
import numpy as np

from OpenGL.GL import *

from look.node import Node
from look.camera import Camera
from look.cursor import Cursor
from look.projection import Projection

from geom.torus import Torus
from geom.cross import Cross

from curves import Curves 
from geom.curve import Curve

import milling_paths

import saver

STARTLOOK = ( (0,0,0) , (0,0,-1) , (0,1,0) )

class Scene :
	DRAW2D , DRAW3D = range(2)
	NONE , CURSOR , TRANSLATE , SCALE , ISOSCALE , ROTATE , CAMERA = range(7)
	PNTBZADD , PNTBSADD , PNTDEL , PNTEDIT = range(4)
	C0 , C1 , C2 = Curves.C0 , Curves.C1 , Curves.C2

	def __init__( self , fov , ratio , near ) :
		self.fov = fov
		self.near = near 
		self.ratio = ratio
		self.drawmode = Scene.DRAW2D
		self.mousemode = Scene.NONE
		self.cursormode = Scene.PNTBZADD

		self.pdist = 0.025
		self.pdist2= self.pdist*self.pdist

		self.root   = Node()
		self.root3d = Node()

		self.camera = Camera()
		self.proj   = Projection()

		self.curves= Curves()

		#
		# craete planes
		#

		self.load_from_file(u'../data/młotek.gpt')
#        self.load_from_file(u'../data/głowica.gpt')
#        self.load_from_file(u'../data/cut_test_10.gpt')

		#
		# Craete torus
		#
		self.torus = Torus()

		self.node = Node()

		tn = Node( self.torus )
		tn.rotate( 3.1415926/2.0 , 1, 0 , 0 )

		self.cursor = Cursor( Cross( self.pdist ) )

		self.node.add_child( tn )
		self.node.add_child( self.cursor )
		self.node.add_child( self.curves )

		#
		# Craete normal scene
		#
		self.proj  .perspective( self.fov , self.ratio, self.near , 10000 )
		self.camera.lookat( *STARTLOOK )
		col = Node( color = (1,1,1) )


		self.root  .add_child( self.proj   )
		self.proj  .add_child( self.camera )
		self.camera.add_child(      col    )
		col        .add_child( self.node   )

		#
		# Create 3d scene
		#
		self.cam_left  = Camera()
		self.cam_right = Camera()
		self.p_left    = Projection()
		self.p_right   = Projection()
		self.t_left    = Node()
		self.t_right   = Node()

		self.root3d.add_child( self.t_left  )
		self.root3d.add_child( self.t_right )

		self.cam_left .lookat( *STARTLOOK )
		self.cam_right.lookat( *STARTLOOK )

		self.p_left .perspective( self.fov , self.ratio, self.near , 10000 )
		self.p_right.perspective( self.fov , self.ratio, self.near , 10000 )

		self.color_left  = Node( color = (1,0,0) )
		self.color_right = Node( color = (0,1,0) )

		self.t_left .add_child( self.p_left  )
		self.t_right.add_child( self.p_right )

		self.p_left .add_child( self.cam_left  )
		self.p_right.add_child( self.cam_right )

		self.cam_left .add_child( self.color_left  )
		self.cam_right.add_child( self.color_right )

		self.color_left .add_child( self.node )
		self.color_right.add_child( self.node )

		self.node.translate(0,0,-2)

	def clear( self ) :
		self.curves.clear()

	def gfx_init( self ) :
		glPointSize(3)

	def draw( self ) :
		root = None

		if self.drawmode == Scene.DRAW2D :
			root = self.root

			glDisable(GL_BLEND)

		elif self.drawmode == Scene.DRAW3D :
			root = self.root3d

			glEnable(GL_BLEND)
			glBlendFunc(GL_ONE,GL_ONE)

		self._draw( root )

		glDisable(GL_BLEND)

	def _draw( self , node ) :
		if not node :
			return

		node.multmatrix()
		node.draw()

		m = glGetFloatv(GL_MODELVIEW_MATRIX)

		for c in node :
			glLoadMatrixf(m)
			self._draw( c )

	def set_left_color( self , color ) :
		self.color_left.set_color( color )

	def set_right_color( self , color ) :
		self.color_right.set_color( color )

	def set_eyes_split( self , split ) :
#        self.cam_left .lookat( (-split,0,0) , (-split,0,-1) , (0,1,0) )
#        self.cam_right.lookat( ( split,0,0) , ( split,0,-1) , (0,1,0) )
		self.cam_left .move( -split , 0 , 0 )
		self.cam_right.move(  split , 0 , 0 )
		self.p_left .loadIdentity()
		self.p_right.loadIdentity()
		self.p_left .translate( -split , 0 , 0 )
		self.p_right.translate(  split , 0 , 0 )

	def _update_proj( self ) :
		self.proj   .perspective( self.fov , self.ratio , self.near , 10000 )
		self.p_left .perspective( self.fov , self.ratio , self.near , 10000 )
		self.p_right.perspective( self.fov , self.ratio , self.near , 10000 )

	def set_fov( self , fov ) :
		self.fov = fov
		self._update_proj()

	def set_near( self , near ) :
		self.near = near
		self._update_proj()

	def set_ratio( self , ratio ) :
		self.ratio = ratio
		self._update_proj()

	def set_screen_size( self , w , h ) :
		self.width  = w 
		self.height = h
		self.curves.set_screen_size( w , h )

	def set_drawmode( self , mode ) :
		self.drawmode = mode

	def set_mousemode( self , mode ) :
		self.mousemode = mode

	def set_cursormode( self , mode ) :
		self.cursormode = mode

	def set_editmode( self , mode ) :
		self.curves.set_editmode( mode )

	def set_lookat( self , pos , look ) :
		pos = np.array(pos)
		look = np.array(look)
		up = np.cross(look,(1,0,0))
		if up[0]==0 and up[1]==0 and up[2]==0 :
			up = np.cross(look,(0,0,1))
		if up[0]==0 and up[1]==0 and up[2]==0 :
			up = np.cross(look,(0,1,0))
		up = up / np.linalg.norm(up)
		self.camera.lookat( pos , pos+look , up )
		self.cam_left .lookat( pos , pos+look , up )
		self.cam_right.lookat( pos , pos+look , up )


	def get_cursor_pos( self ) :
		return self.cursor.get_pos()
	
	def get_cursor_screen_pos( self ) :
		cp = self.cursor.get_clipping_pos()
		return ( (cp[0]+1.0)/2.0 * self.width , (cp[1]+1.0)/2.0 * self.height )

	def mouse_move( self , rdf , df , a1 , a2 ) :

		if self.mousemode == Scene.CURSOR :
			v = self.cursor.move_vec( df )
			self.curves.point_move( v )

		elif self.mousemode == Scene.TRANSLATE :
			self.node.translate( *map(lambda x:x*.01,df) )
		elif self.mousemode == Scene.SCALE :
			self.node.scale( *map(lambda x:1+x*.01,df) )
		elif self.mousemode == Scene.ISOSCALE :
			self.node.scale( *([1+.01*reduce( op.add , df ) ] * 3 ) )
		elif self.mousemode == Scene.ROTATE :
			df.remove(0)
			self.node.rotate( df[0]*.001 , *a1 )
			self.node.rotate( df[1]*.001 , *a2 )
		elif self.mousemode == Scene.CAMERA :
			rdf = [ x*.1 for x in rdf ]
			self.camera.rot( rdf[0] ,-rdf[1] )
			self.cam_left.rot( rdf[0] ,-rdf[1] )
			self.cam_right.rot( rdf[0] ,-rdf[1] )
	
	def key_pressed( self , df ) :
		if self.mousemode == Scene.CAMERA :
			self.camera.move( *map(lambda x : x*.05 , df ) )
			self.cam_left.move( *map(lambda x : x*.05 , df ) )
			self.cam_right.move( *map(lambda x : x*.05 , df ) )

	def activate_cursor( self ) :
		if self.cursormode == Scene.PNTBZADD :
			self.curves.point_new( Curve.BEZIER  , self.cursor.get_pos() )
		elif self.cursormode == Scene.PNTBSADD :
			self.curves.point_new( Curve.BSPLINE , self.cursor.get_pos() )
		elif self.cursormode == Scene.PNTDEL :
			self.curves.point_delete( self.cursor.get_clipping_pos() , self.pdist2 )
		elif self.cursormode == Scene.PNTEDIT :
			self.curves.point_select( self.cursor.get_clipping_pos() , self.pdist2 )

	def new_curve_c0( self ) :
		self.curves.new( self.cursor.get_pos() , Curves.BEZIER_C0 , post_data=Curve.BEZIER ) 

	def new_curve_c2( self ) :
		if self.cursormode == Scene.PNTBZADD :
			self.curves.new( self.cursor.get_pos() , Curves.BEZIER_C2 , post_data=Curve.BEZIER  )
		elif self.cursormode == Scene.PNTBSADD :                      
			self.curves.new( self.cursor.get_pos() , Curves.BEZIER_C2 , post_data=Curve.BSPLINE )

	def new_curve_interpolation( self ) :
		self.curves.new( self.cursor.get_pos() , Curves.INTERPOLATION )

	def new_surface_c0( self , size ) :
		self.curves.new( self.cursor.get_pos() , Curves.SURFACE_C0 , pre_data = size )

	def new_surface_c2( self , size ) :
		self.curves.new( self.cursor.get_pos() , Curves.SURFACE_C2 , pre_data = size )

	def new_pipe( self , size ) :
		self.curves.new( self.cursor.get_pos() , Curves.SURFACE_PIPE , pre_data = size )

	def new_gregory( self , size ) :
		self.curves.new( self.cursor.get_pos() , Curves.SURFACE_GREGORY , pre_data = size )

	def delete_curve( self ) :
		self.curves.delete( self.cursor.get_clipping_pos() , self.pdist2 )

	def select_curve( self ) :
		self.curves.select( self.cursor.get_clipping_pos() , self.pdist2 )

	def toggle_curve( self , which , what ) :
		self.curves.toggle( which , what )

	def fill_gap( self , c ) :
		self.curves.fill_gap( c )

	def cut_current( self , pos , delta ) :
#        return self.curves.cut( self.cursor.get_pos() , delta )
		return self.curves.cut( pos , delta )

	def select_to_cut( self ) :
		self.curves.select_to_cut( self.cursor.get_clipping_pos() , self.pdist2 )

	def clear_cut( self ) :
		self.curves.clear_cut()

	def cut_select( self , i , k ) :
		self.curves.cut_select( i , k )

	def set_surf_density( self , dens ) :
		self.curves.set_surf_density( dens )

	def load_from_file( self , path ) :
		self.curves.load( path )

	def dump_to_file( self , path ) :
		self.curves.dump( path )

	def gen_paths( self ) :
		self.clear()

		self.load_from_file(u'../data/młotek.gpt')
		for c in self.curves : self.curves.cutter.add( c )
		print 'cut'
		self.curves.cut( (0,0,0,0) , 0.01 )
		print 'mil'
		self.miller = milling_paths.Miller( self.curves )
		self.node.add_child( self.miller )

	def dump_sign( self ) :
		curv = self.curves.selected
		if curv == None : return
		path = []
		for u in np.linspace(0,len(curv)-1,len(curv)*16) :
			path.append( curv.get_ptn( u ) )
		trans = np.resize( milling_paths.TRANS , 4 )
		trans[3] = 0
		scale = milling_paths.SCALE
		proc = lambda p : (p + trans)*scale
		saver.save(-1,'05_sign.k4',path, pre = proc )

