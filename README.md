# Torrusador

One semester project on geometry modeling lecture at Warsaw Uniwersity of Technology faculty of Mathematics and Information Science, Speciality CAD/CAM. These project was made in week sprints and we had no idea what exactly would be next. Finally we build simple CAD system in which we ware able to model simple object. On next semester this model was cut on milling cutter. Effect is shown at the end.


## week 1

Simple 3D scene with wireframe torus model. Available was only 'drawline' function so all matrix conversions were to be be done manually.

## week 2

Not related raycasting project <http://github.com/jkotur/ellipsoid>.

## week 3

Stereoscopy view of all object on scene. Currently only torus, but should work with future objects.

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/stereoscopy.png" alt="stereoscopy" width="600" />

## week 4

  * 3D cursor that can be moved in 3 axes aligned to camera local axes. Showing cursor coordinates on scene.
  * adding/removing/moving points on 3D scene with cursor

## week 5

  * adding Bezier curves to scene
  * curves chain are connected with C0 differentiability class
  * curve should be drawn more accurate as observer is getting closer to it

## week 6
  
  * adding Bezier curves chain with C2 class
  * drawing in both Bezier and De Boore basis

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/bezier.png" alt="bezier" width="600" />

## week 7

  * third degree curve that interpolates points with C2 class

## week 8
  
  * bicubic Bezier surfaces
  * surfaces are build with Bezier patches based on 16 points 
  * patches are connected with class C0
  * visualisation with lines of constant parameter
  * adaptive mesh drawing

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/surface.png" alt="surface" width="600" />

## week 9

  * De Boore surfaces with C2 class
  * De Boore pipes also with C2 class
  * file format for saving/loading surfaces and pipes

## week 10, 11
  
  * design model of hammer 
  * model should be build with 2 pipes
  * model must have edge with C0 class
  * saving/loading model

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/hammer.png" alt="hammer" width="600" />

## week 12

  * fill triangle holes with Gregory patches
  * patch should match with C1 and G2 class
  * optionally matching with C2 class

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/gregory_patch.png" alt="gregory_patch" width="600" />

## week 13, 14

Trimming bspline surfaces. User can choose two surfaces and trim one with other. Trimming curve near cursor should be found.

  1. find intersection point with conjugate gradient method
  2. find intersection curve with at least Newtons method
  3. find and show surfaces sections

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/trim_test.png" alt="trimming1" width="400" />
<img src="https://github.com/jkotur/Torrusador/raw/master/screens/trim_hammer.png" alt="trimming2" width="400" />

## Effect

<img src="https://github.com/jkotur/Torrusador/raw/master/screens/effect.png" alt="effect" width="600" />

