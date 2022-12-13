from django import template

register = template.Library()

@register.filter
def replace_space(value):
	n = 0
	s = list(value)

	
	for i in range(10):
		n+=1
		s.insert(n*5, ' ')
	string_con = ''.join(str(e) for e in s)
	return string_con

    	

