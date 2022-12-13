from django import template

register = template.Library()

@register.filter
def sort_string(value):
	value = str(value)


	find_index = value.index('name="')
	find_last_index = value.index('id"')


	
	
	return 'id_'+value[find_index+6:find_last_index]+ 'line_item'