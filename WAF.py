
import re
import datetime
from ParseHTTP import ParseHTTP

class WAF:

	def __init__(self, ip_origin, port_origin, ip_dest, port_dest, log_path):

		self.rules = {}
		self.ip_origin = ip_origin
		self.port_origin = port_origin
		self.ip_dest = ip_dest
		self.port_dest = port_dest
		self.log_path = log_path

	def parse(self, config_file):

		'''
			Esta funcion se encarga de hacer el parseo del archivo de configuracion, guarda todo en un diccionario
			el cual podemos utilizar posteriormente para evaluar que es lo que tenemos que hacer, obtener las
			expresiones regulares etc.
		'''

		with open(config_file, "r") as config_file:
            
			for rule in config_file.readlines():
                
				rule = rule.strip()

				regex = re.search(r'".*"', rule)
				regex = regex.string[regex.regs[0][0]+1:regex.regs[0][1]-1] # Obtiene la expresion regular sin comillas
                
				rule = rule.replace("\""+regex+"\"", '') # Eliminamos la expresion regular de la cadena original

				tmp = rule.split(';') # Queda como csv (;)

				rule_no = int(tmp[0].split('->')[1]) # Obtenemos el numero de regla

				variables = []

				# Obtenemos las variables que esten separadas por pipe

				if len(tmp[1].split('|')) > 1:
					for var in tmp[1].split('|'):
						variables.append(var)
				else:
					variables.append(tmp[1])

				option = tmp[2][0:-1] # Se obtiene la opcion de regex
				description = tmp[3] # Se obtiene la descripcion de la regla

				if len(tmp[4].split(':')) == 2:
					action = tmp[4].split(':')[1]
				else:
					action = tmp[4]
				
				if(rule_no in self.rules.keys()):
					print("\n[Otra regla ya tiene este numero]\n\t{} (No sera tomada en cuenta)\n".format(description))
				else:
					self.rules[rule_no] = { 'rule_no':rule_no, 'variables':variables, 'option':option, 'description':description, 'action':action, 'regex':regex }
	
	def check_filter(self, raw_request):

		'''
			Esta funcion se encarga de evaluar cada una de las reglas, se trata de dos ciclos anidados, uno itera
			entre las reglas y el otro itera dentro de cada regla para cada valor, es decir en que parte de la 
			peticion HTTP tenemos que aplicar la expresion de la regla si en el cuerpo, en alguna cabecera o en
			toda la peticion por ejemplo.		
		'''

		http_request = ParseHTTP()
		http_request.parse(raw_request)

		print("\n" + raw_request.decode('utf-8') + "\n")
					
		#headers = { k.upper():v for k,v in http_request.headers.items() }	# Diccionario de Cabeceras
		headers_val =  list(http_request.headers.values())					# Lista de los valores de las cabeceras
		headers_names = list(http_request.headers.keys())					# Lista de los nombres de las cabeceras
		headers_v_n = headers_val + headers_names;							# Lista valores + nombres de cabeceras

		for rule in self.rules.values():

			# rule es un diccionario que contiene toda la informacion de una regla en especifico
			# entonces este primer for itera sobre todas las reglas  guardadas en self.rules y con
			# la variable rule tenemos acceso a las caracteristicas de la regla para utilizarlas 
			# como y cuando se necesite.

			for var in rule['variables']:

				# rule['variables'] es una lista que guarda los lugares en donde hay que evaluar la
				# expresion regular, puede ser uno o varios, si son varios en el archivo de configuracion
				# se indican separados por un pipe "|"
				
				if(var == 'AGENTE_USUARIO'):
										
					if "User-Agent" in http_request.headers.keys():

						if(rule['option'] == 'iregex'):
							r = re.compile(rule['regex'], re.IGNORECASE)
						else:
							r = re.compile(rule['regex'])

						f = re.search(r, http_request.headers['User-Agent'])

						if(f is not None):

							self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

							action = rule['action']
					
				elif(var == 'METODO'):
										
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					f = re.search(r, raw_request.decode('utf-8'))
					
					if(f is not None):
												
						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'RECURSO'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					f = re.search(r, http_request.resource)

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'CUERPO'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					f = re.search(r, http_request.body)

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'PETICION_LINEA'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					f = re.search(r, http_request.line_req)

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'CLIENTE_IP'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					f = re.search(r, self.ip_origin)

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'CABECERAS_VALORES'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
					
					for element in headers_val:

						f = re.search(r, element)

						if f is not None:
							break

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']


				elif(var == 'CABECERAS_NOMBRES'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					for element in headers_names:

						f = re.search(r, element)

						if f is not None:
							break

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)
						
						action = rule['action']

				elif(var == 'CABECERAS'):
					
					if(rule['option'] == 'iregex'):
						r = re.compile(rule['regex'], re.IGNORECASE)
					else:
						r = re.compile(rule['regex'])
						
					for element in headers_v_n:
						f = re.search(r, element)
						if f is not None:
							break

					if(f is not None):

						self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)

						action = rule['action']

				elif(var == 'COOKIES'):

					if "Cookie" in http_request.headers.keys():
					
						if(rule['option'] == 'iregex'):
							r = re.compile(rule['regex'], re.IGNORECASE)
						else:
							r = re.compile(rule['regex'])
							
						f = re.search(r, http_request.headers['Cookie'])

						if(f is not None):
												
							self.update_log(self.log_path, self.ip_origin, self.port_origin,
												self.ip_dest, self.port_dest, rule['rule_no'],
												rule['description'], raw_request.decode('utf-8'),
												var)
							
							action = rule['action']

		return action

	def update_log(self, log_path, ip_origin, port_origin, ip_dest, port_dest, rule_id, rule_descr, raw_request, location):

		'''
			Esta funcion se encarga de actualizar la agenda cada que se detecta que una peticion debe ser bloqueada
			por algun motivo.
		'''
		
		date = str(datetime.datetime.now())
		
		with open(log_path, "a+") as log:
			log.write("\n" + date + ";" + str(ip_origin) + ";" + str(port_origin) + ";" + str(ip_dest) + ";"
						+ str(port_dest) + ";" + str(rule_id) + ";" + str(rule_descr) + ";" + str(location)
						+ ";\n\n" + raw_request + "\n")