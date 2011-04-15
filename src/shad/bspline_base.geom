#version 330

layout(points) in;
layout(line_strip , max_vertices = 256 ) out;

uniform mat4 modelview;
uniform mat4 projection;
uniform ivec2 screen;

uniform samplerBuffer points;
uniform float base[256];

vec3 pts[32];

#define KNOTSNUM 8 
float knots[KNOTSNUM];

void main()
{
	ivec2 id = ivec2(gl_in[0].gl_Position.xy);

	for( int i=id.x ; i<id.y ; ++i )
		pts[i-id.x] = texelFetch( points , i ).xyz;

	int bblen = 0;
	vec4 a  , b;

	a = projection * modelview * vec4(pts[0],1);
	a/= a.w;
	a.x *= screen.x;
	a.y *= screen.y;
	for( int i=1 ; i<4 ; ++i )
	{
		b = projection * modelview * vec4(pts[i],1);
		b/= b.w;
		b.x *= screen.x;
		b.y *= screen.y;
		bblen += int(distance( a , b ));
		a = b;
	}

	bblen /= 100;

	int nums = max(1,min( bblen , 60 ));
	int di = int(float(60)/float(nums))*4;

	for( int i=0 ; i<256 ; i+=di )
	{
		vec3 pnt = vec3(0);
		for( int j=0 ; j<4 ; ++j )
			pnt += pts[j] * base[i+j];

		gl_Position = projection * modelview * vec4( pnt , 1 );
		EmitVertex();
	}
	EndPrimitive();
}

