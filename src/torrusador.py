import sys

import pygtk
pygtk.require('2.0')
import gtk

import operator as op
from copy import copy

from OpenGL.GL import *

from glwidget import GLDrawingArea

from scene import Scene

from geom.curve import Curve

ui_file = "torrusador.ui"

class App(object):
	"""Application main class"""

	def __init__(self):

		self._init_keyboard() 

		self.near = 1
		self.fov  = 60

		builder = gtk.Builder()
		builder.add_from_file(ui_file)

		glconfig = self.init_glext()

		self.drawing_area = GLDrawingArea(glconfig)
		self.drawing_area.set_events( gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON1_MOTION_MASK)
		self.drawing_area.set_size_request(800, 800)

		self.box3d = builder.get_object("hbox_3d")

		builder.get_object("vbox4").pack_start(self.drawing_area)

		win_main = builder.get_object("win_main")

		win_main.set_events( gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK )
         
		win_main.connect('key-press-event'  , self._on_key_pressed  )
		win_main.connect('key-release-event', self._on_key_released )

		win_main.show_all()
		self.box3d.hide();

		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height
		ratio = float(width)/float(height)

		self.scene = Scene( self.fov , ratio , self.near )
		self.drawing_area.add( self.scene )

		builder.connect_signals(self)

		self.statbar = builder.get_object('statbar')

		self.drawing_area.connect('motion_notify_event',self._on_mouse_motion)
		self.drawing_area.connect('button_press_event',self._on_button_pressed)
		self.drawing_area.connect('configure_event',self._on_reshape)
		self.drawing_area.connect_after('expose_event',self._after_draw)

		self.rbut_trans = builder.get_object('rbut_trans')
		self.rbut_isoscale = builder.get_object('rbut_isoscale')
		self.rbut_scale = builder.get_object('rbut_scale')
		self.rbut_rotate = builder.get_object('rbut_rotate')

		self.rbut_xy = builder.get_object('rbut_xy')
		self.rbut_xz = builder.get_object('rbut_xz')
		self.rbut_yz = builder.get_object('rbut_yz')

		self.sp_fov = builder.get_object('sp_fov')
		self.sp_fov.set_value(self.fov)

		self.sp_near = builder.get_object('sp_near')
		self.sp_near.set_value(self.near)

		self.tbut_add_c0    = builder.get_object('tbut_add_c0'   )
		self.tbut_add_c2    = builder.get_object('tbut_add_c2'   )
		self.tbut_add_inter = builder.get_object('tbut_add_interpolation')
		self.tbut_del_curve = builder.get_object('tbut_del_curve')
		self.tbut_sel_curve = builder.get_object('tbut_sel_curve')

	def _init_keyboard( self ) :
		self.move = [0,0,0]
		self.dirskeys = ( ( ['w'] , ['s'] ) , ( ['a'] , ['d'] ) , ( ['e'] , ['q'] ) )
   
		for d in self.dirskeys :
			for e in d : 
				for i in range(len(e)) : e[i] = ( gtk.gdk.unicode_to_keyval(ord(e[i])) , False )

	def _on_key_pressed( self , widget , data=None ) :
		if not any(self.move) :
			gtk.timeout_add( 20 , self._move_callback )
						  
		for i in range(len(self.dirskeys)) :
			if (data.keyval,False) in self.dirskeys[i][0] :
				self.dirskeys[i][0][ self.dirskeys[i][0].index( (data.keyval,False) ) ] = (data.keyval,True)
				self.move[i]+= 1
			elif (data.keyval,False) in self.dirskeys[i][1] :
				self.dirskeys[i][1][ self.dirskeys[i][1].index( (data.keyval,False) ) ] = (data.keyval,True)
				self.move[i]-= 1
                      
                      
	def _on_key_released( self , widget , data=None ) :
		for i in range(len(self.dirskeys)) :
			if (data.keyval,True) in self.dirskeys[i][0] :
				self.dirskeys[i][0][ self.dirskeys[i][0].index( (data.keyval,True) ) ] = (data.keyval,False)
				self.move[i]-= 1
			elif (data.keyval,True) in self.dirskeys[i][1] :
				self.dirskeys[i][1][ self.dirskeys[i][1].index( (data.keyval,True) ) ] = (data.keyval,False)
				self.move[i]+= 1
                      
	def _move_callback( self ) :
		self.scene.key_pressed( self.move )
		self.drawing_area.queue_draw()
		return any(self.move)

	def _after_draw( self , widget , data=None ) :
		self.update_statusbar()

	def update_statusbar( self ) :
		cid = self.statbar.get_context_id('cursor')
		self.statbar.pop(cid)
		self.statbar.push( cid , str(self.scene.get_cursor_pos()) + "  " + str(self.scene.get_cursor_screen_pos()) )

	def on_tbut_add_c0_toggled( self , widget , data=None ) :
		if self.tbut_add_c0.get_active() :
			self.tbut_add_c2.set_active(False)
			self.tbut_add_inter.set_active(False)
			self.tbut_del_curve.set_active(False)
			self.tbut_sel_curve.set_active(False)

	def on_tbut_add_c2_toggled( self , widget , data=None ) :
		if self.tbut_add_c2.get_active() :
			self.tbut_add_c0.set_active(False)
			self.tbut_add_inter.set_active(False)
			self.tbut_del_curve.set_active(False)
			self.tbut_sel_curve.set_active(False)
	
	def on_tbut_add_interpolation_toggled( self, widget , data=None ) :
		if self.tbut_add_inter.get_active() :
			self.tbut_add_c0.set_active(False)
			self.tbut_add_c2.set_active(False)
			self.tbut_del_curve.set_active(False)
			self.tbut_sel_curve.set_active(False)

	def on_tbut_del_curve_toggled( self , widget , data=None ) :
		if self.tbut_del_curve.get_active() :
			self.tbut_add_c0.set_active(False)
			self.tbut_add_c2.set_active(False)
			self.tbut_add_inter.set_active(False)
			self.tbut_sel_curve.set_active(False)

	def on_tbut_sel_curve_toggled( self , widget , data=None ) :
		if self.tbut_sel_curve.get_active() :
			self.tbut_add_c0.set_active(False)
			self.tbut_add_c2.set_active(False)
			self.tbut_add_inter.set_active(False)
			self.tbut_del_curve.set_active(False)

	def _on_reshape( self , widget , data=None ) :
		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height

		ratio = float(width)/float(height)

		self.scene.set_screen_size( width , height )
		self.scene.set_ratio( ratio )

	def _on_button_pressed( self , widget , data=None ) :
		if data.button == 1 :
			self.mouse_pos = -data.x , data.y
		elif data.button == 3 :
			if self.tbut_add_c0.get_active() :
				self.scene.new_curve_c0()
				self.tbut_add_c0.set_active(False)
			elif self.tbut_add_c2.get_active() :
				self.scene.new_curve_c2()
				self.tbut_add_c2.set_active(False)
			elif self.tbut_add_inter.get_active() :
				self.scene.new_curve_interpolation()
				self.tbut_add_inter.set_active(False)
			elif self.tbut_del_curve.get_active() :
				self.scene.delete_curve()
				self.tbut_del_curve.set_active(False)
			elif self.tbut_sel_curve.get_active() :
				self.scene.select_curve()
				self.tbut_sel_curve.set_active(False)
			else :
				self.scene.activate_cursor()
			self.drawing_area.queue_draw()

	def _on_mouse_motion( self , widget , data=None ) :
		diff = map( op.sub , self.mouse_pos , (-data.x , data.y) )
		rowdiff = copy(diff)

		if self.rbut_xy.get_active() :
			diff[2:2] = [0]
			axis1= ( 0 , 1 , 0 )
			axis2= ( 1 , 0 , 0 )
		elif self.rbut_xz.get_active() :
			diff[1:1] = [0]
			axis1= ( 0 , 0 , 1 )
			axis2= ( 1 , 0 , 0 )
		elif self.rbut_yz.get_active() :
			diff.reverse();
			diff[0:0] = [0]
			axis1= ( 0 , 1 , 0 )
			axis2= ( 0 , 0 , 1 )

		self.scene.mouse_move( rowdiff , diff , axis1 , axis2 )

		self.mouse_pos = -data.x , data.y
		self.drawing_area.queue_draw()
	
	def init_glext(self):
		# Query the OpenGL extension version.
#        print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()

		# Configure OpenGL framebuffer.
		# Try to get a double-buffered framebuffer configuration,
		# if not successful then try to get a single-buffered one.
		display_mode = (gtk.gdkgl.MODE_RGB    |
				gtk.gdkgl.MODE_DEPTH  |
				gtk.gdkgl.MODE_DOUBLE)
		try:
			glconfig = gtk.gdkgl.Config(mode=display_mode)
		except gtk.gdkgl.NoMatches:
			display_mode &= ~gtk.gdkgl.MODE_DOUBLE
			glconfig = gtk.gdkgl.Config(mode=display_mode)

#        print "is RGBA:",                 glconfig.is_rgba()
#        print "is double-buffered:",      glconfig.is_double_buffered()
#        print "is stereo:",               glconfig.is_stereo()
#        print "has alpha:",               glconfig.has_alpha()
#        print "has depth buffer:",        glconfig.has_depth_buffer()
#        print "has stencil buffer:",      glconfig.has_stencil_buffer()
#        print "has accumulation buffer:", glconfig.has_accum_buffer()
#        print

		return glconfig

	def on_win_main_destroy(self,widget,data=None):
		gtk.main_quit()
		 
	def on_but_quit_clicked(self,widget,data=None):
		gtk.main_quit()

	def on_cbut_draw_bezier_pts_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BEZIER , Curve.POINTS )
		self.drawing_area.queue_draw()

	def on_cbut_draw_bezier_curves_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BEZIER , Curve.CURVE )
		self.drawing_area.queue_draw()

	def on_cbut_draw_bezier_polygons_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BEZIER , Curve.POLYGON )
		self.drawing_area.queue_draw()

	def on_cbut_draw_bspline_pts_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BSPLINE , Curve.POINTS )
		self.drawing_area.queue_draw()

	def on_cbut_draw_bspline_curves_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BSPLINE , Curve.CURVE )
		self.drawing_area.queue_draw()

	def on_cbut_draw_bspline_polygons_toggled(self,widget,data=None):
		self.scene.toggle_curve( Curve.BSPLINE , Curve.POLYGON )
		self.drawing_area.queue_draw()

	def on_sp_R_value_changed(self,widget,data=None):
		# FIXME: hardcoded torus
		self.scene.torus.R = widget.get_value()
		self.scene.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_r_value_changed(self,widget,data=None):
		# FIXME: hardcoded torus
		self.scene.torus.r = widget.get_value()
		self.scene.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_N_value_changed(self,widget,data=None):
		# FIXME: hardcoded torus
		self.scene.torus.N = widget.get_value()
		self.scene.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_n_value_changed(self,widget,data=None):
		# FIXME: hardcoded torus
		self.scene.torus.n = widget.get_value()
		self.scene.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_near_value_changed( self, widget , data=None ):
		# FIXME: hardcoded torus
		self.scene.torus.P0  = -widget.get_value()
		self.scene.set_near( widget.get_value() )
		self.drawing_area.queue_draw()

	def on_sp_fov_value_changed(self,widget,data=None):
		self.scene.set_fov( widget.get_value() )
		self.drawing_area.queue_draw()

	def on_chbut_3d_toggled( self , widget , data=None ):
		if self.box3d.get_property("visible") :
			self.box3d.hide()
			self.scene.set_drawmode( Scene.DRAW2D )
		else:
			self.box3d.show()
			self.scene.set_drawmode( Scene.DRAW3D )
		self.drawing_area.queue_draw()

	def on_colbut_right_color_set( self , widget , data=None ):
		CMAX = 65535.0
		c = widget.get_color()
		c = ( c.red / CMAX , c.green / CMAX , c.blue / CMAX )
		self.scene.set_right_color( c )
		self.drawing_area.queue_draw()

	def on_colbut_left_color_set( self , widget , data=None ):
		CMAX = 65535.0
		c = widget.get_color()
		c = ( c.red / CMAX , c.green / CMAX , c.blue / CMAX )
		self.scene.set_left_color( c )
		self.drawing_area.queue_draw()

	def on_hs_3d_value_changed( self , widget , data=None ):
		v = widget.get_value() / 2.0 
		self.scene.set_eyes_split( v )
		self.drawing_area.queue_draw()

	def on_rbut_none_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.NONE )
	def on_rbut_cursor_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.CURSOR )
	def on_rbut_scale_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.SCALE )
	def on_rbut_isoscale_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.ISOSCALE )
	def on_rbut_trans_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.TRANSLATE )
	def on_rbut_rotate_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.ROTATE )
	def on_rbut_camera_pressed( self , widget , data=None ) :
		self.scene.set_mousemode( Scene.CAMERA )

	def on_rbut_pnt_add_bezier_pressed( self , widget , data=None ) :
		self.scene.set_cursormode( Scene.PNTBZADD )
	def on_rbut_pnt_add_bspline_pressed( self , widget , data=None ) :
		self.scene.set_cursormode( Scene.PNTBSADD )
	def on_rbut_pnt_del_pressed( self , widget , data=None ) :
		self.scene.set_cursormode( Scene.PNTDEL )
	def on_rbut_pnt_edit_pressed( self , widget , data=None ) :
		self.scene.set_cursormode( Scene.PNTEDIT )

	def on_show( self , widget , data=None ):
		widget.show_all()

	def on_hide( self , widget , data=None ):
		widget.hide()
		return True

if __name__ == '__main__':
	app = App()
	gtk.main()

