file_type = dict()
file_type['js'] = 'application/javascript'
file_type['json'] = 'application/json'
file_type['zip'] = 'application/zip'
file_type['pdf'] = 'application/pdf'
file_type['sql'] = 'application/sql'
file_type['mpeg'] = 'audio/mpeg'
file_type['ogg'] = 'audio/ogg'
file_type['css'] = 'text/css'
file_type['html'] ='text/html'
file_type['xml'] = 'text/xml'
file_type['csv'] = 'text/csv'
file_type['txt'] = 'text/plain'
file_type['png'] = 'image/png'
file_type['jpg'] = 'image/jpeg'
file_type['gif'] = 'image/gif'

errors_dict = dict()

errors_dict['404'] = []
errors_dict['404'].append(r'HTTP/1.1 404 NotFound\r\n')
errors_dict['404'].append("""<!DOCTYPE html>
<html>
<title> ERROR </title>
<body>
<h1>404</h1>
<p>The server can not find the requested page..</p>
</body>
</html>""")

errors_dict['403'] = []
errors_dict['403'].append(r'HTTP/1.1 403 Forbidden\r\n')
errors_dict['403'].append("""<!DOCTYPE html>
<html>
<title> ERROR </title>
<body>
<h1>403</h1>
<p>Access is forbidden to the requested page.</p>
</body>
</html>""")

errors_dict['405'] = []
errors_dict['405'].append(r'HTTP/1.1 405 MethodNotAllowed\r\n')
errors_dict['405'].append("""<!DOCTYPE html>
<html>
<title> ERROR </title>
<body>
<h1>405</h1>
<p>The method specified in the request is not allowed.</p>
</body>
</html>""")
errors_dict['500'] = []
errors_dict['500'].append(r'HTTP/1.1 500 InternalServerError\r\n')
errors_dict['500'].append("""<!DOCTYPE html>
<html>
<title> ERROR </title>
<body>
<h1>500</h1>
<p>The request was not completed. The server met an unexpected condition or the script can't be executed.</p>
</body>
</html>""")
