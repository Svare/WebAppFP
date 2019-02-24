class ParseHTTP():
	
	def parse(self, raw):

		'''
			Esta clase se encarga de parsear toda la peticion HTTP descomponiendola
			en sus partes mas sencillas como body, headers, method etc. y las almacena
			en variables de clase para tenerlas disponibles cuando las necesitemos.
		'''

		raw_lines = raw.splitlines(True)
		raw_lines = [line.decode('utf-8') for line in raw_lines]

		self.line_req = raw_lines[0].strip()						# Primera linea de la peticion
		self.method = raw_lines[0].strip().split(' ')[0]            # Cadena que guarda el metodo
		self.requested_URL = raw_lines[0].strip().split(' ')[1]     # Cadena que guarda la URL solicitada
		self.HTTP_version = raw_lines[0].strip().split(' ')[2]      # Cadena que guarda la version HTTP
		
		i = 1 # iterador
		self.headers = {} # Diccionario que guarda los encabezados
		
		while(raw_lines[i].strip() != ''):
			self.headers[raw_lines[i].strip().split(': ')[0]] = raw_lines[i].strip().split(': ')[1]
			i += 1
		
		self.body = '' # Cadena que guarda el cuerpo de la peticion
		
		for j in range(i, len(raw_lines)):
			self.body += raw_lines[j]
		
		self.body = self.body.strip()
		
		self.get_params()

	def get_params(self):
		
		self.params = {}
		
		if self.method == "GET" or self.method == "HEAD":

			try:

				if len(self.requested_URL.split('?')) == 2 :
				
					self.relative_path = self.requested_URL.split('?')[0]
					self.query_string = self.requested_URL.split('?')[1]
					
					for param in self.requested_URL.split('?')[1].split('&'):
						if '=' in param: 
							self.params[param.split('=')[0]] = param.split('=')[1]
				else:
					
					self.relative_path = self.requested_URL
					self.query_string = ''
					self.params = {}
				
			except Exception as e:

				print(e)
	
		elif self.method == "POST":
			if len(self.body.split('&')) > 1:
				self.query_string = self.body
				for param in self.body.split('&'):
					self.params[param.split('=')[0]] = param.split('=')[1]
			else:
				if self.body != '':
					self.query_string = self.body
					self.params[self.body.split('=')[0]] = self.body.split('=')[1]
				else:
					self.query_string = ''
			
			self.relative_path = self.requested_URL           # Ruta Relativa
		else:
			self.relative_path = ''
			self.query_string = ''
		
		self.resource = self.relative_path.split('/')[-1]     # Nombre del archivo
		self.extension = self.resource.split('.')[-1]         # Nombre extension