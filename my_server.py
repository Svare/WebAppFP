#!/usr/bin/python3
import os
import socket
import optparse
import sys
from errores import errors_dict, file_type
from ParseHTTP import ParseHTTP
from WAF import WAF
import subprocess 


class HTTPWebServer(object):
	def __init__(self, port, root_dir, logs_dir, waf_conf, waf_log):
		self.serversocket = None
		self.ip = socket.gethostbyname('localhost')
		self.port = port
		self.root_dir = root_dir
		self.logs_dir = logs_dir
		self.http_request = ParseHTTP()
		self.sub_env = dict()
		self.message = ''
		self.waf_conf = waf_conf
		self.waf_log = waf_log
	
	#metodo generico para enviar mensajes al log de errores
	#ya sea al stdout o a un archivo que se indica al correr el server
	def errorLog(self):
		if self.logs_dir:
			with open( self.logs_dir + '/' + 'error.log','a+') as fl:
				fl.write(self.message)
		else:
			print(self.message)
	
	#Similar al error log con la diferencia de que genera logs de exito		
	def accessLog(self):
		if self.logs_dir:
			with open( self.logs_dir + '/' + 'access.log','a+') as fl:
				fl.write(self.message)
		else:
			print(self.message)
	
	#Funcion que combate los ataque de traversal path
	def validateResourceURL(self,resource):
		if '../' in resource:
			return True
		return False
	
	#funcion que comprueba que si la ruta pasada como argumento 
	#es un archivo 
	def isAfile(self,resource):
		return os.path.isfile(resource)
	
	#funcion generica que envia al cliente asociado con clientsocket
	# una respuesta http contruida con los parametros title headers body
	def sendHTTPResponse(self,clientsocket,title, headers, body):
		clientsocket.send((title+headers+body).encode())
	
	#funcion que maneja las peticiones GET
	def getMethod(self, clientsocket):
		
		#Como no se permite indexado de directorios comprueba que el 
		#recurso solicidato tenga un . en su nombre si no lo contiene 
		#envia HTTP error y desecha la peticion
		if not '.' in self.http_request.resource:
			self.message = '403'
			self.sendHTTPResponse(clientsocket, errors_dict['403'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['403'][1])
			return
			
		#Busca que el archivo sea un cgi, si es asi lo ejecuta 
		#mediante la clase subproces y atrapa los errores que pueda 
		#arrojar el script
		try:
			if self.http_request.extension == 'cgi':
				proc, error = subprocess.Popen([self.root_dir + self.http_request.relative_path , self.http_request.query_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=self.sub_env).communicate()
				if error:
					raise Exception("ERROR: cgi")
				self.message = '200'
				clientsocket.send('HTTP/1.1 200 OK\r\n'.encode())
				clientsocket.send(proc)
				return
		except Exception as e:
			self.message = '500'
			self.sendHTTPResponse(clientsocket, errors_dict['500'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['500'][1])
			return
			
		#busca un error de tipo de arhivo porque un navegador no soporta todos los tipos de archivos
		if not self.http_request.extension in file_type.keys():
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])
			return
				
		#verificia que sea un archivo el recurso solicitado y envia sus datos al navegador.
		if self.isAfile(self.root_dir + self.http_request.relative_path):
			self.message = '200'
			clientsocket.send('HTTP/1.1 200 OK\r\n'.encode())
			clientsocket.send('Content-Type: {}\r\n\r\n'.format(file_type[self.http_request.extension]).encode())
			with open(self.root_dir+self.http_request.relative_path,'rb') as fl:
				rd = fl.read()
				clientsocket.send(rd)
		#si no es archivo error
		else:
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])
	
	#funcion que maneja las peticiones POST
	def postMethod(self, clientsocket):
		#Como no se permite indexado de directorios comprueba que el 
		#recurso solicidato tenga un . en su nombre si no lo contiene 
		#envia HTTP error y desecha la peticion
		if not '.' in self.http_request.resource:
			self.message = '403'
			self.sendHTTPResponse(clientsocket, errors_dict['403'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['403'][1])
			return
		#Busca que el archivo sea un cgi, si es asi lo ejecuta 
		#mediante la clase subproces y atrapa los errores que pueda 
		#arrojar el script
		try:
			if self.http_request.extension == 'cgi':
				proc = subprocess.Popen([self.root_dir + self.http_request.relative_path ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE ,env=self.sub_env)
				(grep_stdout, error_cgi) = proc.communicate(input=self.http_request.query_string.encode())
				if error_cgi:
					raise Exception("ERROR:CGI")
				self.message = '200'
				clientsocket.send('HTTP/1.1 200 OK\r\n'.encode())
				clientsocket.send(grep_stdout)
				return
		except Exception as e:
			self.message = '500'
			self.sendHTTPResponse(clientsocket, errors_dict['500'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['500'][1])
			return
		
		#busca un error de tipo de arhivo porque un navegador no soporta todos los tipos de archivos
		if not self.http_request.extension in file_type.keys():
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])
			return
				
		#verificia que sea un archivo el recurso solicitado y envia sus datos al navegador.
		if self.isAfile(self.root_dir + self.http_request.relative_path):
			self.message = '200'
			clientsocket.send('HTTP/1.1 200 OK\r\n'.encode())
			clientsocket.send('Content-Type: {}\r\n\r\n'.format(file_type[self.http_request.extension]).encode())
			with open(self.root_dir+self.http_request.relative_path,'rb') as fl:
				rd = fl.read()
				clientsocket.send(rd)
		#si no es archivo error
		else:
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])
	#funcion que maneja las peticiones HEAD
	def headMethod(self, clientsocket):
		#realiza las mismas acciones que GET pero sin devolver contenido en el cuerpo de la respuesta
		if not '.' in self.http_request.resource:
			self.message = '403'
			self.sendHTTPResponse(clientsocket, errors_dict['403'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['403'][1])
			return

		#busca un error porque un navegador no soporta todos los tipos de archivos
		if not self.http_request.extension in file_type.keys():
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])
			return
		
		#verificia que sea un archivo lo lee y envia para render
		if self.isAfile(self.root_dir + self.http_request.relative_path):
			self.message = '200'
			clientsocket.send('HTTP/1.1 200 OK\r\n'.encode())
			clientsocket.send('Content-Type: {}\r\n\r\n'.format(file_type[self.http_request.extension]).encode())
		#si no es archivo error
		else:
			self.message = '404'
			self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1])

	# se encarga de llenar estas variables al momento de leer una peticion
	def setEnviroment(self, address):
		self.sub_env['DOCUMENT_ROOT'] = self.root_dir
		self.sub_env['HTTP_COOKIE'] = 'gh98qhgh4q9g498hqw4gq'
		self.sub_env['HTTP_REFERER'] = self.http_request.headers['Referer'] if 'Referer' in self.http_request.headers.keys() else ''
		self.sub_env['HTTP_USER_AGENT'] = self.http_request.headers['User-Agent']
		self.sub_env['QUERY_STRING '] = self.http_request.query_string
		self.sub_env['REMOTE_ADDR'] = address[0]
		self.sub_env['REMOTE_PORT'] = str(address[0])
		self.sub_env['REQUEST_METHOD'] = self.http_request.method
		self.sub_env['SERVER_NAME'] = socket.gethostname()
		self.sub_env['SERVER_PORT'] = str(self.port)
		self.sub_env['SERVER_SOFTWARE'] = 'Cranson'

	# funcion que levanta el server y contiene el loop principal para 
	#escuchar conexiones.
	def setUpServer(self):
		#Creamos el socket
		self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#Enlazamos el socket con el puerto y la ip
		try:
			self.serversocket.bind((self.ip, self.port))
			#print("Socket bind")
		except Exception as e:
			print("No se pudo realizar el socket bind en el puerto:{}".format(self.port))
			sys.exit(1)
			
		#Ponemos a escuchar en el la ip y puerto establecidos
		self.serversocket.listen(5)
		print("\nHTTP Server escuchando en -> {}:{}".format(self.ip,self.port))

		#cliclo infinito para nuevas conexiones.
		while True:
			clientsocket, address = self.serversocket.accept()
			data = clientsocket.recv(1024)
			
			if not data: break
			#Llamamos a la funcion parser
			self.http_request.parse(data)
			self.setEnviroment(address)

			###################################################
			################## WAF ############################
			###################################################

			if self.waf_conf is not None:

				waf = WAF(self.ip, self.port, self.sub_env['REMOTE_ADDR'], self.sub_env['REMOTE_PORT'], self.waf_log) # Parametros del Constructor
				waf.parse(self.waf_conf) # Cargamos el archivo de configuracion
				action = waf.check_filter(data)
			
				if(action == "404"):
					self.sendHTTPResponse(clientsocket, errors_dict['404'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['404'][1] )
					continue
				elif(action == "500"):
					self.sendHTTPResponse(clientsocket, errors_dict['500'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['500'][1] )
					continue
				elif(action == "ignorar"):
					continue

			###################################################

			elif self.validateResourceURL(self.http_request.requested_URL):
				#Error con la url
				self.message = '403'
				self.sendHTTPResponse(clientsocket, errors_dict['403'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['403'][1] )
			elif self.http_request.method == 'GET':
				#llama al metodo get
				self.getMethod(clientsocket)
			elif self.http_request.method == 'POST':
				#llama al metodo post
				self.postMethod(clientsocket)
			elif self.http_request.method == 'HEAD':
				#llama la metodo head
				self.headMethod(clientsocket)
			else:
				#Lanza un error porque el server solo escuchar por GET,POST y HEAD
				self.message = '405'
				self.sendHTTPResponse(clientsocket, errors_dict['405'][0], 'Server: MyServer\r\nContent-Type: text/html\r\n\r\n', errors_dict['405'][1] )
				
			clientsocket.close()
			#Registra en los logs por cada peticion que llega, puede ser
			#de exito o de error
			if self.message[0] == '5' or self.message[0] == '4':
				self.message =  str(address[0]) + ' ' + self.message + ' ' +self.http_request.requested_URL
				self.errorLog()
			else:
				self.message =  str(address[0]) + ' ' + self.message + ' ' +self.http_request.requested_URL
				self.accessLog()
				


def read_flags():
	#nos permite leer parametros desde la linea de comandos de una manera
	#mas sencilla y organizada
	parser = optparse.OptionParser()
	parser.add_option('-p', '--port', dest='port', default=8080, help='Server Port.')
	parser.add_option('-d', '--dir', dest='dir', default=os.getcwd(), help='Base Directory.')
	parser.add_option('-l', '--log-dir', dest='logs_dir', default=False, help='Logs Directory')
	parser.add_option('--waf-conf', dest='waf_conf', default=None, help='WAF Config File')
	parser.add_option('--waf-log', dest='waf_log', default="audit.log", help='WAF Log File')
	opts, args = parser.parse_args()
	
	return opts


if __name__ == '__main__':
	
	opts = read_flags()
	
	#Se intenta abrir el directorio pasado mediante el parametro -d que
	# sera el directorio actual de trabajo. Si no se pasa este parametro
	# el servidor tomara como direcotio actual de trabajo al directorio 
	# donde se ejecuto este.
	#Tambien se intenta leer el directorio de los si este es pasado como 
	#parametro
	try:
		os.chdir(opts.dir)
		if opts.logs_dir:
			if not os.path.isdir(opts.logs_dir):
				raise Exception("Path is not a directory")
	except Exception as e:
		print(e)
		print("ERROR: Root dir o logs dir invalidos")
		sys.exit(1)
		
	# Se crea un objeto del servidor web y se levanta.
	server = HTTPWebServer(int(opts.port) , os.getcwd(),  opts.logs_dir, opts.waf_conf, opts.waf_log)
	try:
		server.setUpServer()
	except Exception as e:
		print(str(e))
		server.serversocket.shutdown(socket.SHUT_RDWR)


