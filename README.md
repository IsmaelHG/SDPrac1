# SDPrac1

Practica 1 de Sistemas Distribuidos

Ismael y Gabriel

El master se ejecuta sin parametros

Create Worker:

client.py --wcreate (retorna en pantalla el id del worker)

List Workers:

client.py --wlist

Delete worker:

client.py --wdelete WORKER_ID

Submit CountingWords:

client.py --runcw [url1,url2,...]

Submit WordCount:

client.py --runwc [url1,url2,...]

Ejemplo conteo palabras en ingles:
El resultado debería ser 466550

client.py --runcw [https://raw.githubusercontent.com/dwyl/english-words/master/words.txt]
