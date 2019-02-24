# WebAppFP
Proyecto Final | Servidor Web + WAF

Ejecucion:

	Si deseeamos saber cuales son las opciones de ejecucion disponible basta con
	ejecutar el comando "python3 my_server.py -h" y se desplegara algo como lo siguiente:

	Options:

		  -h, --help						show this help message and exit
		  -p PORT, --port=PORT  			Server Port.
		  -d DIR, --dir=DIR     			Base Directory.
		  -l LOGS_DIR, --log-dir=LOGS_DIR	Logs Directory
		  --waf-conf=WAF_CONF   			WAF Config File
		  --waf-log=WAF_LOG     			WAF Log File

	Como podemos observar ahí se muestra una breve descripcion de lo que hace cada una de las
	banderas y basta con colocar alguna de ellas para comprobar el funcionamiento.

	WAF

		El waf funciona unicamente si la bandera --waf-conf es especificada, a continuación de
		esta bandera debe de colocarse el nombre del archivo que tiene las reglas a considerar
		del waf si no se especifica dicho archivo el servidor fallara así como cuando estan mal
		escritas las reglas.

		Cuando se usa el waf la bandera --waf-log puede no ser especificada, si no se especifica
		el log se llamara "audit.log" por defecto, en caso de que se especifique un nombre el log
		tendra ese nombre.

		ADVERTENCIA: El waf devolvera el error de la ultima regla evaluada para que el server lo
						tome en cuenta y responda acorde a dicho error, los valores de error que
						se consideraron son 404, 500 e ignorar.

	Se proporciona un archivo de configuracion del waf llamado test del cual ha sido probado un
	funcionamiento correcto, la prueba se realizo con curl como cliente con el siguiente comando:

	curl -d "Obviamente no vamos a intentar nada malo aqui <script> alert(1); </script>" -H "Cookie: hex=adecimal; yo=5235423 ; tu=35452 ; beast_no=666" -H "Header-Test: Negron(){echo;} echo; XD" -H "User-Agent: No es XXS <script> alert(1); </script> XD" -H "Johnny-Sins: El Pelon de Brazzers" -X GET "http://127.0.0.1:9092/mi_cuerpo.txt"

	El archivo audit.log es el resultado de probar con este cliente.

	Para probar correr el servidor de la siguiente forma:

	python3 my_server.py --waf-conf test -p 9092