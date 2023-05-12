#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# aplicacion.py: 
# Programa python para manexar unha base de datos de coches.
#
# Autores: Carlos Fernández Armán (carlos.fernandez.arman@udc.es)
#          Tomás Romay Agra (t.ragra@udc.es)
# Data de creación: 12-05-2023
#

import psycopg2
import psycopg2.extensions
import psycopg2.extras
import psycopg2.errorcodes
import sys
import datetime
from decimal import Decimal 

## ------------------------------------------------------------
def connect_db():
    try:
        conn = psycopg2.connect("")
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Non podo conectar: {e}. Abortando programa")
        sys.exit(1)

## ------------------------------------------------------------
def disconnect_db(conn):
    conn.rollback()
    conn.close()

## ------------------------------------------------------------

def alta_vehiculo(conn):
    """
    Pide por teclado os datos dun vehiculo e insértao na táboa
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    marcamodelo=input("Marca/Modelo: ")
    if marcamodelo=="": marcamodelo=None
    sano=input("Ano: ")
    ano = None if sano=="" else int(sano)
    cor=input("Cor: ")
    if cor=="": cor=None
    skms=input("Kms: ")
    kms = None if skms=="" else int(skms)
    sprezo=input("Prezo: ")
    prezo = None if sprezo=="" else float(sprezo)
    


    sql = "insert into vehiculo (marcamodelo,ano,cor,kms,prezo) values(%(m)s, %(a)s, %(c)s, %(k)s,%(p)s)"
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'m': marcamodelo, 'a': ano, 'c': cor, 'k': kms, 'p': prezo})
            conn.commit()
            print("Vehiculo engadido.")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("A táboa vehiculo non existe. NON se pode engadir o vehiculo.") 
            elif e.pgcode== psycopg2.errorcodes.NUMERIC_VALUE_OUT_OF_RANGE:
                print("O prezo máximo son 10 millons")
            elif e.pgcode== psycopg2.errorcodes.CHECK_VIOLATION:
                if 'c_vehiculo_ano_valido' in e.pgerror:
                    print("O ano do vehículo ten que ser válido ( Posterior a 1886 e anterior ou igual ao ano actual ).")
                elif 'c_vehiculo_prezo_valido' in e.pgerror:
                    print("Os prezo do vehículo non pode ser negativo")
                else :
                    print("Os kms do vehículo non poden ser negativos")
            elif e.pgcode== psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if 'marcamodelo' in e.pgerror:
                    print("A Marca/modelo do vehículo é necesaria.")
                elif 'cor' in e.pgerror:
                    print("A Cor do vehículo é necesaria.")
                elif 'ano' in e.pgerror:
                    print("O Ano do vehículo é necesario.")
                elif 'kms' in e.pgerror:
                    print("Os Kms do vehículo son necesarios.")
                else:
                    print("O prezo do vehiculo é necesario")
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------

def engadir_accesorio(conn):
    """
    Pide por teclado o id dun vehiculo e o nome do accesorio que se quere engadir e engádeo ao vehículo
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    
    sid=input("Id do Vehículo: ")
    id = None if sid=="" else int(sid)
    nome=input("Nome do accesorio: ")
    if nome=="": nome=None
    
    sql = "insert into accesorio (nome,id_vehiculo) values(%(n)s, %(i)s)"
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'n': nome, 'i': id})
            conn.commit()
            print("Accesorio engadido.")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("A táboa accesorio non existe. NON se pode engadir o accesorio.") 
            elif e.pgcode== psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
                print(f"O vehículo con id = {id} non existe.")
            elif e.pgcode== psycopg2.errorcodes.NOT_NULL_VIOLATION:
                print("O nome do accesorio é necesario")
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------
def engadir_comprador(conn, control_tx=True):
    """
    Pide por teclado os datos dun comprador e engádeo a bd
    :param conn: a conexión aberta á bd
    :return: Nada
    """
       
    nome=input("Nome: ")
    if nome=="": nome=None
    dni=input("DNI: ")
    if dni=="": dni=None
    direccion=input("Dirección: ")
    if direccion=="": direccion=None
    telefono=input("Teléfono: ")
    if telefono=="": telefono=None
    
    sql = "insert into comprador (nome,dni,direccion,telefono) values(%(n)s, %(dn)s , %(dr)s, %(t)s)"
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'n': nome, 'dn': dni,'dr': direccion,'t': telefono})
            if control_tx:
                conn.commit()
                return dni
            print("Comprador engadido.")        
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("A táboa comprador non existe. NON se pode engadir o comprador.") 
            elif e.pgcode== psycopg2.errorcodes.UNIQUE_VIOLATION:
                print(f"Xa existe un comprador con DNI {dni} , non se engade o comprador")
            elif e.pgcode== psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if 'dni' in e.pgerror:
                    print("O DNI do comprador é necesario.")
                else :
                    print("O Nome do comprador é necesario.")
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()

## ------------------------------------------------------------

def buscar_comprador(conn):
    """
    Pide por teclado o DNI dun comprador e búscao
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    dni=input("DNI: ")
    if dni=="": dni=None
    
    sql = "select dni, nome , direccion , telefono from comprador where dni = %(d)s"

    retval = None
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        try:
            cursor.execute(sql, {'d':dni} )
            row=cursor.fetchone()
            if row is None:
                print("O artigo non existe")
            else:
                telefono = "Descoñecido" if row['telefono'] is None else row["telefono"]
                direccion = "Descoñecido" if row['direccion'] is None else row["direccion"]
                print(f""" Nome: {row['nome']}     DNI: {row['dni']}    
                Direccion: {direccion}
                Telefono: {telefono}""")
            conn.commit()
        except psycopg2.Error as e:
            print(f"Erro {e.pgcode}: {e.pgerror}")
            
            conn.rollback()

def listar_vehiculos(conn):
    """
    Lista todos os vehiculos da BD
    :param conn: a conexión aberta á bd
    :return: Nada
    """

    sql = "select id, marcamodelo , ano , cor , kms , prezo , datacompra from vehiculo order by datacompra desc ,id asc"

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        try:
            cursor.execute(sql)
            rows=cursor.fetchall()
            print(f"Atopados {cursor.rowcount} vehiculos.")
            print("------------------------------------------------------------------------------------")
            for row in rows:
                datacompra = "Non Comprado" if row['datacompra'] is None else (row["datacompra"])       
                print(f"""Marca/Modelo: {row['marcamodelo']}     id: {row['id']}     datacompra: {datacompra}    
                Ano: {row['ano']}   Cor: {row['cor']}   Kms: {row['kms']}  Prezo: {row['prezo']}
                ------------------------------------------------------------------------------------
                """)

            conn.commit()
        except psycopg2.Error as e:
            print(f"Erro {e.pgcode}: {e.pgerror}")
            
            conn.rollback()
            
## ------------------------------------------------------------

def buscar_vehiculos(conn):
    """
    Lista todos os vehiculos dunha Marca/Modelo dispoñibles para a súa compra da BD
    :param conn: a conexión aberta á bd
    :return: Nada
    """

    marcamodelo=input("Marca/Modelo: ")
    if marcamodelo=="": marcamodelo=None

    sql = "select id, marcamodelo , ano , cor , kms , prezo from vehiculo  where  marcamodelo = %(m)s and id_comprador is null order by marcamodelo asc ,datacompra desc , id asc"

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        try:
            cursor.execute(sql, {'m': marcamodelo})
            rows=cursor.fetchall()
            if cursor.rowcount == 0 :
                print("Non hai vehiculos de esta marca/modelo dispoñibles para comprar")
            else :
                print(f"Atopados {cursor.rowcount} vehiculos.")
                print("------------------------------------------------------------------------------------")
                for row in rows:   
                    print(f"""Marca/Modelo: {row['marcamodelo']}     id: {row['id']}      
                    Ano: {row['ano']}   Cor: {row['cor']}   Kms: {row['kms']}  Prezo: {row['prezo']}
                    ------------------------------------------------------------------------------------
                    """)

            conn.commit()
        except psycopg2.Error as e:
            print(f"Erro {e.pgcode}: {e.pgerror}")
            
            conn.rollback()
            
## ------------------------------------------------------------

def comprar_vehiculo(conn):
    """
    Pide por teclado o id dun vehiculo e os datos dun comprador e compra o vehículo.
    Se non existe un comprador crease
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    
    # Preguntamos se existe o comprador
    existsstr=input("Existe o Comprador[S/n]: ")
    exists = resposta_a_boolean(existsstr,True)
    
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
    
    # Se non existe comprador creamolo
    if not exists :
        print("Introduce os datos do comprador:")
        dni=engadir_comprador(conn,False)
        print("-------------------------------------------------")
    else :
        sdni=input("DNI do usuario: : ")
        dni = None if sdni=="" else int(sdni)
     
    # Buscamos o id do comprador    
    sql = "select id from comprador where dni = '%(d)s' "
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        try:
            cursor.execute(sql,{'d': dni})
            row=cursor.fetchone()
            if row is None:
                # Se non existe dni salimos da funcion
                print("O DNI non existe")
                conn.rollback()
                return
            else :
                idcomprador=row['id']
        except psycopg2.Error as e: 
            if e.pgcode == psycopg2.errorcodes.SERIALIZATION_FAILURE:
                print("Non se pode modificar o prezo porque outro usuario o modificou.")
            else :
                print(f"Erro {e.pgcode}: {e.pgerror}")
                conn.rollback()
                return
        
    # Id Vehiculo
    sid=input("Id do Vehículo: ")
    idvehiculo = None if sid=="" else int(sid)
    
    datacompra = datetime.date.today()
    
    # Comprobamos que o vehiculo non foi comprado
    sql = "select id_comprador from vehiculo where id = %(i)s "
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'i': idvehiculo})
            row=cursor.fetchone()
            if row is None :
                print("O Vehículo non existe")
                conn.rollback()
                return
            else :
                if row[0] != None :
                    print(f"O Vehículo con id {idvehiculo} xa foi comprado")
                    conn.rollback()
                    return
                           
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.SERIALIZATION_FAILURE:
                print("Non se pode modificar o prezo porque outro usuario o modificou.")   
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
                conn.rollback()
            return
            
            
    # Actualizamos o vehiculo para compralo
    sql = "update vehiculo set id_comprador = %(ic)s , datacompra = %(d)s where id = %(iv)s"
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'ic': idcomprador, 'd': datacompra,'iv': idvehiculo})
            conn.commit()
            print("Vehiculo comprado.")        
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.SERIALIZATION_FAILURE:
                print("Non se pode modificar o prezo porque outro usuario o modificou.")   
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
                conn.rollback()
            


## ------------------------------------------------------------

def borrar_vehiculo(conn) :
    """
    Pide por teclado o id dun vehiculo e bórrao 
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    sid=input("Id Vehiculo: ")
    id = None if sid=="" else int(sid)

    sql = "delete from vehiculo where id = %(i)s"

    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'i': id} )
            conn.commit()
            if cursor.rowcount == 0:
                print("O vehiculo non existe.")
            else:
                print("Vehiculo borrado")
        except psycopg2.Error as e:
            print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------

def editar_kms(conn):
    """
    Edita os kms dun vehículo
    :param conn: a conexión aberta á bd
    :return: Nada
    """

    sid=input("Id do Vehículo: ")
    id = None if sid=="" else int(sid)
    skms=input("Novos kms: ")
    kms = None if skms=="" else int(skms)
    

    sql = """
            update vehiculo
            set kms = %(k)s
            where id = %(i)s
        """
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'k': kms, 'i': id})
            conn.commit()
            if cursor.rowcount == 0:
                print("O vehiculo non existe.")
            else :
                print("Vehículo modificado.")
        except psycopg2.Error as e:
            if e.pgcode== psycopg2.errorcodes.CHECK_VIOLATION:
                print("Os kms do vehículo non poden ser negativos")
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------

def incrementar_prezo(conn):
    """
    Chama a show_row para pedir un id e mostrar os detalles dun vehiculo, 
    pide incremento para o prezo, e actualiza o vehiculo
    :param conn: a conexión aberta á bd
    :return: Nada
    """

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)

    sid=input("Id do Vehículo: ")
    id = None if sid=="" else int(sid)
    
    sql = "select prezo from vehiculo where id = %(i)s "
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'i': id})
            row=cursor.fetchone()
            if row is None :
                print("O Vehículo non existe")
                conn.rollback()
                return  
            prezo=row[0]               
        except psycopg2.Error as e:   
            print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()
            return
    print(f"O prezo actual do vehiculo id[{id}] é de {prezo}")

    sincr=input("Incremento de prezo (porcentaxe): ")
    incr = None if sincr=="" else float(sincr)


    sql = """
            update vehiculo
            set prezo = prezo + prezo * %(in)s / 100
            where id = %(id)s
        """
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql, {'id': id, 'in':incr})
            conn.commit()
            novoprezo = prezo + (prezo * Decimal(incr/100))
            print(f"Prezo modificado , o novo prezo debería de ser {novoprezo}.")
        except psycopg2.Error as e:
            if e.pgcode== psycopg2.errorcodes.CHECK_VIOLATION:
                print("O prezo debe ser positivo, non se modifica o artigo")
            elif e.pgcode== psycopg2.errorcodes.NUMERIC_VALUE_OUT_OF_RANGE:
                print("O prezo máximo son 10 millons")
            elif e.pgcode == psycopg2.errorcodes.SERIALIZATION_FAILURE:
                print("Non se pode modificar o prezo porque outro usuario o modificou.")
            else:
                print(f"Erro {e.pgcode}: {e.pgerror}")
            conn.rollback()



## ------------------------------------------------------------

def resposta_a_boolean(resposta,default=False) :
    if str.capitalize(resposta) == 'S' :
        return True
    if str.capitalize(resposta) == 'N' :
        return False
    else :
        return default
    
## ------------------------------------------------------------   
    
def menu(conn):
    """
    Imprime un menú de opcións, solicita a opción e executa a función asociada.
    'q' para saír.
    """
    MENU_TEXT = """
      -- MENÚ --
1- Dar de alta vehiculo            2- Engadir accesorio a vehiculo  
3- Engadir comprador               4- Buscar comprador por DNI    
5- Listar todos os vehiculos       6- Buscar vehiculo por Marca/Modelo         
7- Comprar vehiculo                8- Borrar Vehiculo 
9- Cambiar kms vehiculo            0- Incrementar prezo Vehiculo nun porcentaxe 
q - Saír   
"""
    while True:
        print(MENU_TEXT)
        tecla = input('Opción> ')
        if tecla == 'q':
            break
        elif tecla == '1':
            alta_vehiculo(conn)  
        elif tecla == '2':
            engadir_accesorio(conn)
        elif tecla == '3':
            engadir_comprador(conn) 
        elif tecla == '4':
            buscar_comprador(conn)  
        elif tecla == '5':
            listar_vehiculos(conn) 
        elif tecla == '6':
            buscar_vehiculos(conn)  
        elif tecla == '7':
            comprar_vehiculo(conn)  
        elif tecla == '8':
            borrar_vehiculo(conn) 
        elif tecla == '9':
            editar_kms(conn)  
        elif tecla == '0':
            incrementar_prezo(conn) 
            
            
## ------------------------------------------------------------
def main():
    """
    Función principal. Conecta á bd e executa o menú.
    Cando sae do menú, desconecta da bd e remata o programa
    """
    print('Conectando a PosgreSQL...')
    conn = connect_db()
    print('Conectado.')
    menu(conn)
    disconnect_db(conn)

## ------------------------------------------------------------

if __name__ == '__main__':
    main()
