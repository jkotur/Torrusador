import sys

import pygtk
pygtk.require('2.0')
import gtk

import operator as op

from glwidget import GLDrawingArea

from scene.scene import Scene
from scene.node import Node
from scene.camera import Camera
from geom.torus import Torus

ui_file = "torrusador.ui"

class App(object):
	"""Application main class"""

	def __init__(self):

		builder = gtk.Builder()
		builder.add_from_file(ui_file)

		vbox = builder.get_object("box_main")

		glconfig = self.init_glext()

		self.drawing_area = GLDrawingArea(glconfig)
		self.drawing_area.set_events( gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON1_MOTION_MASK)
		self.drawing_area.set_size_request(800, 800)

		vbox.pack_start(self.drawing_area)

		builder.connect_signals(self)

		builder.get_object("win_main").show_all()

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

		self.camera.perspective( self.sp_fov.get_value() , ratio , .1 , 100 )

	def _on_button_pressed( self , widget , data=None ) :
		if data.button != 1 :
			return
		self.node.pos = -data.x , data.y

	def _on_mouse_motion( self , widget , data=None ) :
		if self.rbut_xy.get_active() :
			diff = map( op.sub , self.node.pos , (-data.x , data.y) )
			diff[2:2] = [0]
			axis1= ( 0 , 1 , 0 )
			axis2= ( 1 , 0 , 0 )
		elif self.rbut_xz.get_active() :
			diff = map( op.sub , self.node.pos , (-data.x , data.y) )
			diff[1:1] = [0]
			axis1= ( 0 , 0 , 1 )
			axis2= ( 1 , 0 , 0 )
		elif self.rbut_yz.get_active() :
			diff = map( op.sub , self.node.pos , (-data.x , data.y) )
			diff.reverse();
			diff[0:0] = [0]
			axis1= ( 0 , 1 , 0 )
			axis2= ( 0 , 0 , 1 )

		if self.rbut_trans.get_active() :
			self.node.translate( *map(lambda x:x*.01,diff) )
		elif self.rbut_scale.get_active() :
			self.node.scale( *map(lambda x:1+x*.01,diff) )
		elif self.rbut_isoscale.get_active() :
			self.node.scale( *[1+.01*(reduce( op.add , map( op.sub , self.node.pos , (data.x , -data.y) ) ) ) ] * 3 )
		elif self.rbut_rotate.get_active():
			self.node.rotate(-(self.node.pos[0] + data.x)*.001 , *axis1 )
			self.node.rotate( (self.node.pos[1] - data.y)*.001 , *axis2 )

		self.node.pos = -data.x , data.y
		self.drawing_area.queue_draw()
	
	def init_scene( self ) :
		self.camera = Camera()

		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height
		ratio = float(width)/float(height)

		self.camera.fov = 60
		self.camera.near = 1

		self.camera.perspective( 60 , ratio , 1 , 10000 )
		self.camera.lookat( (0,0,0) , (0,0,-1) , (0,1,0) )

		self.torus = Torus()

		self.node = Node( self.torus )

		self.camera.add_child( self.node )

		self.scene = Scene( self.camera )

		self.drawing_area.add( self.scene )

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

		self.camera.perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.drawing_area.queue_draw()

	def on_sp_near_value_changed( self, widget , data=None ):
		width = self.drawing_area.allocation.width
		height = self.drawing_area.allocation.height

		ratio = float(width)/float(height)

		self.camera.near = widget.get_value()
		self.torus.P0  = -widget.get_value()

		self.camera.perspective( self.camera.fov , ratio , self.camera.near , 10000 )
		self.drawing_area.queue_draw()

if __name__ == '__main__':
	app = App()
	gtk.main()

