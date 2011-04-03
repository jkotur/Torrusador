#version 330

layout(points) in;
layout(line_strip , max_vertices = 256 ) out;

uniform mat4 modelview;
uniform mat4 projection;

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

	for( float t=0.0 ; t<=1.0 ; t+=.00390625 )
	{
		gl_Position = vec4(
				decasteljau(t,casx,len),
				decasteljau(t,casy,len),
				decasteljau(t,casz,len),1);
//		gl_Position = vec4(
//				mix(casx[0],casx[len-1],t),
//				mix(casy[0],casy[len-1],t),
//				mix(casz[0],casz[len-1],t),1);
		gl_Position =  projection * modelview * gl_Position;
		EmitVertex();
	}
	EndPrimitive();
}

