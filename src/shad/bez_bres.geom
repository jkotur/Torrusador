#version 330

layout(points) in;
layout(line_strip , max_vertices = 256 ) out;

uniform mat4 modelview;
uniform mat4 projection;
uniform ivec2 screen;

uniform samplerBuffer points;

float casx[32];
float casy[32];
float casz[32];
float tmp[32];

float decasteljau( float t , float pts[32] , int len )
{
	for( int i=0 ; i<32 ; ++i )
		tmp[i] = 0.0;

	for( int i=len-1 ; i>=0 ; --i )
		tmp[i] = pts[i];

	float t1 = 1.0-t;
	for( int k=len-1 ; k>0 ; --k )
		for( int i=0 ; i<k ; ++i )
			tmp[i] = tmp[i]*t1 + tmp[i+1]*t;
	return tmp[0];
}

void main()
{
	ivec2 id = ivec2(gl_in[0].gl_Position.xy);

	int len = id.y - id.x;

	for( int i=id.x ; i<id.y ; ++i )
	{
		vec4 ptn = texelFetch( points , i );

		casx[i-id.x] = ptn.x;
		casy[i-id.x] = ptn.y;
		casz[i-id.x] = ptn.z;
	}

	int bblen = 0;

	vec4 a  , b;

	a = projection * modelview * vec4(casx[0],casy[0],casz[0],1);
	a/= a.w;
	a.x *= screen.x;
	a.y *= screen.y;
	for( int i=1 ; i<len ; ++i )
	{
		b = projection * modelview * vec4(casx[i],casy[i],casz[i],1);
		b/= b.w;
		b.x *= screen.x;
		b.y *= screen.y;
		bblen += int(distance( a , b ));
		a = b;
	}

	bblen /= 25;

	int nums = max(1,min( bblen , 255 ));
	float dt = 1.0/nums;

	for( float t=0.0 ; t<1.0+dt ; t+=dt )
	{
		gl_Position = vec4(
				decasteljau(t,casx,len),
				decasteljau(t,casy,len),
				decasteljau(t,casz,len),1);
		gl_Position =  projection * modelview * gl_Position;
		EmitVertex();
	}
	EndPrimitive();
}

