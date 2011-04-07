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

#define KNOTSNUM 6
float knots[KNOTSNUM];

float calca( float t , int i , int k  , int n , float knots[KNOTSNUM] )
{
	return ( t - knots[i] ) / ( knots[i+n+1-k] - knots[i] );
}

float decasteljau( float t , float pts[32] , int n , float knots[KNOTSNUM] )
{
	for( int i=0 ; i<32 ; ++i )
		tmp[i] = 0.0;

	for( int i=n-1 ; i>=0 ; --i )
		tmp[i] = pts[i];
	
	int l=0;
	while( knots[l+1] < t ) ++l;

	l = 3;
	n = 3;

	for( int k=1 ; k<n ; ++k )
		for( int i=l-n+k ; i<l ; ++ i )
		{
			float a  = calca( t , i , k , n , knots );
			tmp[i] = tmp[i-1]*(1.0-a) + tmp[i]*a;
		}
	return tmp[n-1];
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


	float u  = 0.0;
	float du = 1.0/KNOTSNUM;
	for( int i=0 ; i<KNOTSNUM ; i++ )
	{
		knots[i] = u;
		u += du;
	}

	float dt = du/64;
	for( float t=knots[3] ; t<knots[4]+dt ; t+=dt )
	{
		gl_Position = vec4(
				decasteljau(t,casx,len,knots),
				decasteljau(t,casy,len,knots),
				decasteljau(t,casz,len,knots),1);
		gl_Position =  projection * modelview * gl_Position;
		EmitVertex();
	}
	EndPrimitive();
}

