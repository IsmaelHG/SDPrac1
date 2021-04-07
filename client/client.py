# ---------------------------------------------------------------------------------------------------------------------
# SISTEMAS DISTRIBUIDOS
# Gabriel Garcia, Ismael El-Fellah
# Fichero que expone la utilidad de invocar a las funciones de la api master a traves de los parametros:
#       --wcreate : crea worker
#       --wdelete <idworker> : elimina worker correspondiente a idworker
#       --wlist: lista workers
#       --runCW [paramsURL] : llama a counting words con los parametros indicados entre los corchetes
#       --runWC [paramsURL] : llama a word count con los parametros indicados entre los corchetes
#
# ---------------------------------------------------------------------------------------------------------------------
import xmlrpc.client
import click

@click.command()
@click.option('--wcreate', default=1, help='Crea un worker')

def wcreate(wcreate):
    if wcreate !
    pass


if __name__ == '__main__':
    proxy = xmlrpc.client.ServerProxy('http://localhost:9000')
    print(proxy.submit_countingwords("[http://localhost:8000/fitxer1, http://localhost:8000/fitxer2]"))


