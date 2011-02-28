import sys

import pygtk
pygtk.require('2.0')
import gtk

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
		self.drawing_area.set_size_request(800, 800)

		vbox.pack_start(self.drawing_area)

		builder.connect_signals(self)

		builder.get_object("win_main").show_all()

		self.init_scene()
	
	def init_scene( self ) :
		self.camera = Camera()
		self.camera.projection( 60 , 1 , 1 , 10000 )
		self.camera.lookat( (10,0,5) , (0,0,0) , (-1,0,0) )

		self.torus = Torus()

		node = Node( self.torus )
#        node.m = [ [1,0,0,0] , [0,1,0,0] , [0,0,1,0] , [0,0,-5,1] ]

		self.camera.add_child( node )

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

if __name__ == '__main__':
	app = App()
	gtk.main()

