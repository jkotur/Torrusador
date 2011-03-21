
from OpenGL.GL import *

from look.node import Node
from look.camera import Camera
from look.cursor import Cursor
from look.projection import Projection
from look.color import Color

from geom.torus import Torus
from geom.point import Point

from points import Points

class Scene :
	DRAW2D , DRAW3D = range(2)
	NONE , CURSOR , TRANSLATE , SCALE , ISOSCALE , ROTATE = range(6)
	PNTADD , PNTDEL , PNTEDIT = range(3)

	def __init__( self , fov , ratio , near ) :
		self.fov = fov
		self.near = near 
		self.ratio = ratio
		self.drawmode = Scene.DRAW2D
		self.mousemode = Scene.NONE
		self.cursormode = Scene.PNTADD

		self.root   = Node()
		self.root3d = Node()

		self.camera = Camera()
		self.proj   = Projection()

		self.points = Points()

		#
		# Craete torus
		#
		self.torus = Torus()

		self.node = Node()

		tn = Node( self.torus )
		tn.rotate( 3.1415926/2.0 , 1, 0 , 0 )

		self.cursor = Cursor( Point() , self.node )

		self.node.add_child( tn )
		self.node.add_child( self.cursor )
		self.node.add_child( self.points )

		#
		# Craete normal scene
		#
		self.proj  .perspective( self.fov , self.ratio, self.near , 10000 )
		self.camera.lookat( (0,0,0) , (0,0,-1) , (0,1,0) )
		col = Color( (1,1,1) )


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

		self.cam_left .lookat( (0,0,0) , (0,0,-1) , (0,1,0) )
		self.cam_right.lookat( (0,0,0) , (0,0,-1) , (0,1,0) )

		self.p_left .perspective( self.fov , self.ratio, self.near , 10000 )
		self.p_right.perspective( self.fov , self.ratio, self.near , 10000 )

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

	def gfx_init( self ) :
		glPointSize(2)

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
		self.cam_left .lookat( (-split,0,0) , (-split,0,-1) , (0,1,0) )
		self.cam_right.lookat( ( split,0,0) , ( split,0,-1) , (0,1,0) )
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

	def set_drawmode( self , mode ) :
		self.drawmode = mode

	def set_mousemode( self , mode ) :
		self.mousemode = mode

	def set_cursormode( self , mode ) :
		self.cursormode = mode

	def get_cursor_pos( self ) :
		return self.cursor.get_pos()

	def mouse_move( self , df , a1 , a2 ) :

		if self.mousemode == Scene.CURSOR :
			self.cursor.move_vec( df )

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

	def activate_cursor( self ) :
		if self.cursormode == Scene.PNTADD :
			self.points.new( self.cursor.get_pos() )
		elif self.cursormode == Scene.PNTDEL :
			self.points.delete( self.cursor.get_pos() )
		elif self.cursormode == Scene.PNTEDIT :
			self.points.select( self.cursor.get_pos() )

