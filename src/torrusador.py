import sys

import pygtk
pygtk.require('2.0')
import gtk

import operator as op

from OpenGL.GL import *

from glwidget import GLDrawingArea

from scene.scene import Scene
from scene.node import Node
from scene.camera import Camera
from scene.color import Color
from scene.projection import Projection
from geom.torus import Torus

ui_file = "torrusador.ui"

class App(object):
	"""Application main class"""

	def __init__(self):

		builder = gtk.Builder()
		builder.add_from_file(ui_file)

		glconfig = self.init_glext()

		self.drawing_area = GLDrawingArea(glconfig)
		self.drawing_area.set_events( gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON1_MOTION_MASK)
		self.drawing_area.set_size_request(800, 800)

		self.box3d = builder.get_object("hbox_3d")

		builder.get_object("vbox4").pack_start(self.drawing_area)

		builder.connect_signals(self)

		builder.get_object("win_main").show_all()
		self.box3d.hide();

		self.init_scene()

		self.drawing_area.connect('motion_notify_event',self._on_mouse_motion)
		self.drawing_area.connect('button_press_event',self._on_button_pressed)
		self.drawing_area.connect('configure_event',self._on_reshape)

		self.rbut_trans = builder.get_object('rbut_trans')
		self.rbut_isoscale = builder.get_object('rbut_isoscale')
		self.rbut_scale = builder.get_object('rbut_scale')
		self.rbut_rotate = builder.get_object('rbut_rotate')

		self.rbut_xy = builder.get_object('rbut_xy')
		self.rbut_xz = builder.get_object('rbut_xz')
		self.rbut_yz = builder.get_object('rbut_yz')

		self.sp_fov = builder.get_object('sp_fov')
		self.sp_fov.set_value(60)

		builder.get_object('sp_near').set_value(1)

	def _on_reshape( self , widget , data=None ) :

		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height

		ratio = float(width)/float(height)

		self.proj   .perspective( self.sp_fov.get_value() , ratio , 10 , 100 )
		self.p_left .perspective( self.sp_fov.get_value() , ratio , 10 , 100 )
		self.p_right.perspective( self.sp_fov.get_value() , ratio , 10 , 100 )

	def _on_button_pressed( self , widget , data=None ) :
		if data.button != 1 :
			return
		self.node.pos = -data.x , data.y

	def _on_mouse_motion( self , widget , data=None ) :
		diff = map( op.sub , self.node.pos , (-data.x , data.y) )

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

#        print diff
#        print reduce( op.add , diff ) 
#        print [ 1+.01*reduce( op.add , diff ) ] * 3
#        print map(lambda x:1+x*.01,diff)

		if self.rbut_trans.get_active() :
			self.node.translate( *map(lambda x:x*.01,diff) )
		elif self.rbut_scale.get_active() :
			self.node.scale( *map(lambda x:1+x*.01,diff) )
		elif self.rbut_isoscale.get_active() :
			self.node.scale( *([1+.01*reduce( op.add , diff ) ] * 3 ) )
		elif self.rbut_rotate.get_active():
			self.node.rotate(-(self.node.pos[0] + data.x)*.001 , *axis1 )
			self.node.rotate( (self.node.pos[1] - data.y)*.001 , *axis2 )

		self.node.pos = -data.x , data.y
		self.drawing_area.queue_draw()
	
	def init_scene( self ) :
		self.camera = Camera()
		self.proj   = Projection()

		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height
		ratio = float(width)/float(height)

		#
		# Craete torus
		#
		self.torus = Torus()

		self.node = Node( self.torus )
		self.node.rotate( 3.1415926/2.0 , 1, 0 , 0 )
		self.camera.fov = 60
		self.camera.near = 1

		#
		# Craete normal scene
		#
		self.proj  .perspective( 60 , ratio , 1 , 10000 )
		self.camera.lookat( (0,0,0) , (0,0,-1) , (0,1,0) )
		col = Color( (1,1,1) )

		self.proj  .add_child( self.camera )
		self.camera.add_child(      col    )
		col        .add_child( self.node   )

		self.scn_one    = Scene( self.proj )

		#
		# Create 3d scene
		#
		self.cam_left  = Camera()
		self.cam_right = Camera()
		self.p_left    = Projection()
		self.p_right   = Projection()
		self.t_left    = Node()
		self.t_right   = Node()

		root = Node()
		root.add_child( self.t_left  )
		root.add_child( self.t_right )

		self.cam_left .lookat( (0,0,0) , (0,0,-1) , (0,1,0) )
		self.cam_right.lookat( (0,0,0) , (0,0,-1) , (0,1,0) )

		self.p_left .perspective( 60 , ratio , 1 , 10000 )
		self.p_right.perspective( 60 , ratio , 1 , 10000 )

		self.color_left  = Color( (1,0,0) )
		self.color_right = Color( (0,1,0) )

		self.t_left .add_child( self.p_left  )
		self.t_right.add_child( self.p_right )

		self.p_left .add_child( self.cam_left  )
		self.p_right.add_child( self.cam_right )

		self.cam_left .add_child( self.color_left  )
		self.cam_right.add_child( self.color_right )

		self.color_left .add_child( self.node )
		self.color_right.add_child( self.node )

		self.scn_double = Scene( root )

		self.drawing_area.add( self.scn_one )

	def init_glext(self):
		# Query the OpenGL extension version.
		print "OpenGL extension version - %d.%d\n" % gtk.gdkgl.query_version()

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

		print "is RGBA:",                 glconfig.is_rgba()
		print "is double-buffered:",      glconfig.is_double_buffered()
		print "is stereo:",               glconfig.is_stereo()
		print "has alpha:",               glconfig.has_alpha()
		print "has depth buffer:",        glconfig.has_depth_buffer()
		print "has stencil buffer:",      glconfig.has_stencil_buffer()
		print "has accumulation buffer:", glconfig.has_accum_buffer()
		print

		return glconfig

	def on_win_main_destroy(self,widget,data=None):
		gtk.main_quit()
		 
	def on_but_quit_clicked(self,widget,data=None):
		gtk.main_quit()

	def on_sp_R_value_changed(self,widget,data=None):
		self.torus.R = widget.get_value()
		self.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_r_value_changed(self,widget,data=None):
		self.torus.r = widget.get_value()
		self.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_N_value_changed(self,widget,data=None):
		self.torus.N = widget.get_value()
		self.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_n_value_changed(self,widget,data=None):
		self.torus.n = widget.get_value()
		self.torus.refresh()
		self.drawing_area.queue_draw()

	def on_sp_fov_value_changed(self,widget,data=None):
		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height

		ratio = float(width)/float(height)

		self.camera.fov = widget.get_value()

		self.proj   .perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.p_left .perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.p_right.perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.drawing_area.queue_draw()

	def on_sp_near_value_changed( self, widget , data=None ):
		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height

		ratio = float(width)/float(height)

		self.camera.near = widget.get_value()
		self.torus.P0  = -widget.get_value()

		self.proj   .perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.p_left .perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.p_right.perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.drawing_area.queue_draw()

	def set_2d( self ) :
		self.drawing_area.remove( self.scn_double )
		self.drawing_area.add   ( self.scn_one    )

		glDisable(GL_BLEND)
	
	def set_3d( self ) :
		self.drawing_area.remove( self.scn_one    )
		self.drawing_area.add   ( self.scn_double )

		glEnable(GL_BLEND)
		glBlendFunc(GL_ONE,GL_ONE)

	def on_chbut_3d_toggled( self , widget , data=None ):
		if self.box3d.get_property("visible") :
			self.box3d.hide()
			self.set_2d()
		else:
			self.box3d.show()
			self.set_3d()
		self.drawing_area.queue_draw()

	def on_colbut_right_color_set( self , widget , data=None ):
		CMAX = 65535.0
		c = widget.get_color()
		c = ( c.red / CMAX , c.green / CMAX , c.blue / CMAX )
		self.color_right.set_color( c )
		self.drawing_area.queue_draw()

	def on_colbut_left_color_set( self , widget , data=None ):
		CMAX = 65535.0
		c = widget.get_color()
		c = ( c.red / CMAX , c.green / CMAX , c.blue / CMAX )
		self.color_left.set_color( c )
		self.drawing_area.queue_draw()

	def on_hs_3d_value_changed( self , widget , data=None ):
		v = widget.get_value() / 2.0 #/ 20.0
		self.cam_left .lookat( (-v,0,0) , (-v,0,-1) , (0,1,0) )
		self.cam_right.lookat( ( v,0,0) , ( v,0,-1) , (0,1,0) )
		self.p_left .loadIdentity()
		self.p_right.loadIdentity()
		self.p_left .translate( -v , 0 , 0 )
		self.p_right.translate(  v , 0 , 0 )
		self.drawing_area.queue_draw()

if __name__ == '__main__':
	app = App()
	gtk.main()

