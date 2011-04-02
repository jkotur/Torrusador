#version 330

layout(points) in;
layout(points , max_vertices = 1) out;

uniform mat4 modelview;
uniform mat4 projection;

uniform samplerBuffer points;

void main()
{
	int id = int( gl_in[0].gl_Position.x) ;

	vec4 pos = texelFetch( points , id );
	pos.w = 1;

	gl_Position = projection * modelview * pos;
	EmitVertex();
	EndPrimitive();
}

