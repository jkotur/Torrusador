import sys

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gtkgl

from OpenGL.GL import *
from OpenGL.GLU import *

ui_file = "torrusador.ui"

class SimpleDrawingArea(gtk.DrawingArea, gtk.gtkgl.Widget):
	"""OpenGL drawing area for simple demo."""
	def __init__(self, glconfig):
		gtk.DrawingArea.__init__(self)

		# Set OpenGL-capability to the drawing area
		self.set_gl_capability(glconfig)

		# Connect the relevant signals.
		self.connect_after('realize',   self._on_realize)
		self.connect('configure_event', self._on_configure_event)
		self.connect('expose_event',    self._on_expose_event)

	def _on_realize(self, *args):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = self.get_gl_drawable()
		glcontext = self.get_gl_context()

		# OpenGL begin.
		if not gldrawable.gl_begin(glcontext):
			return

		# OpenGL end
		gldrawable.gl_end()

	def _on_configure_event(self, *args):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = self.get_gl_drawable()
		glcontext = self.get_gl_context()

		self.width = self.allocation.width
		self.height = self.allocation.height

		# OpenGL begin
		if not gldrawable.gl_begin(glcontext):
			return False

		glViewport(0, 0, self.allocation.width, self.allocation.height)

		# OpenGL end
		gldrawable.gl_end()

		return False

	def _on_expose_event(self, *args):
		# Obtain a reference to the OpenGL drawable
		# and rendering context.
		gldrawable = self.get_gl_drawable()
		glcontext = self.get_gl_context()

		# OpenGL begin
		if not gldrawable.gl_begin(glcontext):
			return False

		if gldrawable.is_double_buffered():
			gldrawable.swap_buffers()
		else:
			glFlush()

		# OpenGL end
		gldrawable.gl_end()

		return False

class App(object):
	"""Application main class"""

	def __init__(self):
		builder = gtk.Builder()
		builder.add_from_file(ui_file)

		vbox = builder.get_object("vbox_main")

		glconfig = self.init_glext()

		self.drawing_area = SimpleDrawingArea(glconfig)
		self.drawing_area.set_size_request(800, 800)

		vbox.pack_start(self.drawing_area)

		hbox = builder.get_object("vbox_chart")

		builder.connect_signals(self)

		builder.get_object("win_main").show_all()

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


if __name__ == '__main__':
	app = App()
	gtk.main()

