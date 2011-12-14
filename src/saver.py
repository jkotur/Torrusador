import math as m

def save( num , filename , paths , pre = None ) :
	with open(filename,'w+') as f :
		i = 0
		for p in paths if num < 0 else paths[num] :
			if pre != None : p = pre( p )
			f.write( 'N%dG01X%fY%fZ%f\n' % ( i , p[0] , p[1] ,-p[2] ) )
			i+=1

def save_commpressed( num , filename , paths , pre = None ) :
	pp = None
	with open(filename,'w+') as f :
		i = 0
		for p in paths if num < 0 else paths[num] :
			if pre != None : p = pre( p )
			f.write( 'N%dG01' % i )
			if pp != None and m.fabs( pp[0] - p[0] ) > 1.0 :
				f.write( 'X%f' % p[0] )
			if pp != None and m.fabs( pp[1] - p[1] ) > 1.0 :
				f.write( 'Y%f' % p[1] )
			if pp != None and m.fabs( pp[2] - p[2] ) > 1.0 :
				f.write( 'Z%f' % -p[2] )
			f.write('\n')
			pp = p
			i+=1
