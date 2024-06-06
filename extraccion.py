import pandas as pd
import numpy as np
from datetime import datetime

# Leer pdf
import PyPDF2
#import pdfplumber
import fitz  # PyMuPDF
#from pdfminer.high_level import extract_text
import PyPDF4
import slate3k as slate

# Procesamiento texto
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import unicodedata

# Guardar archivos
import pickle

# Base de datos sql
import mysql.connector

# Buscar provincia a través de código postal
import pgeocode


# Script
import argparse
import os

# Función para leer una factura:
def ft_readinvoice(path, name):
    invoices = {}
    errors = {}
    count = 0
    try:
        with open(path, 'rb') as file:
            print(name)
            reader = PyPDF2.PdfReader(file)
            # Obtén el número de páginas
            num_pages = len(reader.pages)
            content = {}
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                content[page_num] = text
            invoices[0] = content
        with open(f"{name}.pkl", 'wb') as file:
            pickle.dump(invoices, file)
    except:
        print("""Error al leer la factura. 
            Comprueba que el archivo esté en el mismo directorio, 
            que el nombre del archivo sea válido (sin la extensión) 
            y que el archivo sea formato pdf""")
        errors[count] = name
        count += 1
        
    return invoices

# Función normalización de factura
def ft_cleaner(text):
    # Eliminar saltos de línea y tabuladores
    text = re.sub(r'[\n\t]', ' ', text)
    
    # Normalizar el texto (NFKD) y eliminar diacríticos (acentos)
    normalize_text = unicodedata.normalize('NFKD', text)
    text_tilde = ''.join(c for c in normalize_text if not unicodedata.combining(c))
    
    # Eliminar caracteres especiales adicionales, dejando solo letras, dígitos, espacios, guiones, comillas simples y comas
    final_text = re.sub(r"[^A-Za-z0-9\s\',/.]", '', text_tilde)
    
    # Quitar espacios adicionales
    final_text = ' '.join(final_text.split())

    final_text = final_text.lower()
    
    return final_text

# Función para obtener factura normalizada
def ft_normalize(name):
    print(name)
    
    pickle_file = f"{name}.pkl"
    with open(pickle_file, 'rb') as file:
        invoices = pickle.load(file)
        
    clean_invoices = {}

    for tittle, pages in invoices.items():
        clean_pages = {}
        for num_pages, content in pages.items():
            clean_pages[num_pages] = ft_cleaner(content)
            #clean_pages[num_pages] = unicodedata.normalize('NFKD', content)
        clean_invoices[tittle] = clean_pages
    clean_invoices = clean_invoices[0]

    # Guardar el diccionario en un archivo
    with open(f'{name}_limpia.pkl', 'wb') as file:
        pickle.dump(clean_invoices, file)
    
    return clean_invoices

def encontrar_provincia_por_cp(codigo_postal, pais='ES'):
    # Crear un objeto Nominatim para el país especificado (por defecto España)
    nomi = pgeocode.Nominatim(pais)
    
    # Obtener la información geográfica del código postal
    info = nomi.query_postal_code(codigo_postal)
    
    # Verificar si se encontró información válida
    if info.county_name:
        return info.county_name
    else:
        return "none"
    
def ft_font_code(invoice, name):

    result = {}

    invoices = {}
    client_name = []
    dni = []
    adress_street = []
    adress_city = []
    adress_province = []
    adress_cp = []
    distributor_name = []
    cif = []
    distributor_city = []
    distributor_street = []
    distributor_province = []
    distributor_cp = []

    pages = invoice

    for n_pages, content in pages.items():
    
        # -----------------------------------------------------------------------------------------------------------
        # Client name
        patron_cn_1 = r'nombre (.*?) direccion'
        matches_1 = re.findall(patron_cn_1, content, re.IGNORECASE)
        for match in matches_1:
            if match:
                client_name.extend(matches_1)
        
        patron_cn_2 = r'titular del contrato (.*?) nif'
        matches_2 = re.findall(patron_cn_2, content, re.IGNORECASE)
        for match in matches_2:
            if match not in client_name:  # Solo agregar si no está en matches_1
                client_name.append(match)
        patron_cn_3 = r'titular(?! del contrato)(.*?)nif'
        matches_3 = re.findall(patron_cn_3, content, re.IGNORECASE)
        for match in matches_3:
            if match not in client_name:  # Solo agregar si no está en matches_1
                client_name.append(match)
        invoices["nombre_cliente"] = client_name[:]
        
        # ----------------------------------------------------------------------------------------------------------------------------
        # DNI   
        patron_nif = r'nif (\d{8}[a-zA-Z])'
        nif_1 = re.findall(patron_nif, content, re.IGNORECASE)
        for match in nif_1:
            if match not in dni:
                dni.extend(nif_1)
        invoices["dni_cliente"] = dni[:]

        #-----------------------------------------------------------------------------------------------------------------------------
        # Adress, city, province, cp
        patron_adress_1 = r"direccion\sde\ssuministro\s(?P<calle>.+?),\s(?P<localidad>.+?),\s(?P<provincia>.+?)\snumero\sde\scontador"
        adress_1 = re.search(patron_adress_1, content)
        if adress_1:
            if "calle_cliente" not in invoices:
                adress_street.append(adress_1.group("calle"))
                invoices["calle_cliente"] = adress_street
            if "población_cliente" not in invoices:
                adress_city.append(adress_1.group("localidad"))
                invoices["población_cliente"] = adress_city
            if "provincia_cliente" not in invoices:
                adress_province.append(adress_1.group("provincia"))
                invoices["provincia_cliente"] = adress_province

            # Patrón para encontrar el código postal entre la calle y la localidad
            if (n_pages >= 1):
                # Looking for cp from street
                found_street = adress_1.group("calle")
                found_city = adress_1.group("localidad")
                # Crear un patrón que busque el código postal entre la calle y la localidad
                patron_cp = fr'{re.escape(found_street)}\s+(\d{{5}})\s+{re.escape(found_city)}'
                cp_match = re.search(patron_cp, pages[n_pages - 1])

                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp
            if (invoices["nombre_cliente"]):
                found_client_name = invoices["nombre_cliente"][0]  # Suponiendo que solo hay un nombre almacenado en la lista
                # Patrón para encontrar el código postal después del nombre del cliente
                patron_cp = fr'{re.escape(found_client_name)}.*?(\d{{5}})'
                cp_match = re.search(patron_cp, pages[n_pages])
                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp

        patron_adress_2 = r"direccion\s+suministro\s+(?P<calle>.+?)\s+(?P<codigo_postal>\d{5})\s+(?P<localidad>.+?)\b"
        adress_2 = re.search(patron_adress_2, content)
        if adress_2:
            if "calle_cliente" not in invoices:
                adress_street.append(adress_2.group("calle"))
                invoices["calle_cliente"] = adress_street
            if "cp_cliente" not in invoices:
                adress_cp.append(adress_2.group("codigo_postal"))
                invoices["cp_cliente"] = adress_cp
            if "población_cliente" not in invoices:
                adress_city.append(adress_2.group("localidad"))
                invoices["población_cliente"] = adress_city
            # Patrón para encontrar el código postal entre la calle y la localidad
            if (n_pages >= 1):
                # Looking for cp from street
                found_street = adress_2.group("calle")
                found_city = adress_2.group("localidad")
                # Crear un patrón que busque el código postal entre la calle y la localidad
                patron_cp = fr'{re.escape(found_street)}\s+(\d{{5}})\s+{re.escape(found_city)}'
                cp_match = re.search(patron_cp, content)

                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp
            if (invoices["nombre_cliente"]):
                found_client_name = invoices["nombre_cliente"][0]
                patron_cp = fr'{re.escape(found_client_name)}.*?(\d{{5}})'
                cp_match = re.search(patron_cp, pages[n_pages])
                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp

        patron_adress = r"direccion de suministro\s+(?P<calle>.+?),\s+(?P<poblacion>.+?),\s+(?P<provincia>\w+)\s+numero de contador"
        adress_match = re.search(patron_adress, content)

        if adress_match:
            if "calle_cliente" not in invoices:
                adress_street.append(adress_match.group("calle"))
                invoices["calle_cliente"] = adress_street

            poblacion = adress_match.group("poblacion")
            if "población_cliente" not in invoices:
                invoices["población_cliente"] = [poblacion]
            elif len(poblacion) < len(invoices["población_cliente"][0]):
                invoices["población_cliente"] = [poblacion]

            if "provincia_cliente" not in invoices:
                adress_province.append(adress_match.group("provincia"))
                invoices["provincia_cliente"] = adress_province

        patron_direccion = r"calle\s+(?P<calle>.+?)\s+(?P<cp>\d{5})\s+(?P<localidad>.+?)\s+(?P<provincia>\w+)$"
        direccion_match = re.match(patron_direccion, content)

        if direccion_match:
            if "calle_cliente" not in invoices:
                adress_street.append(direccion_match.group("calle"))
                invoices["calle_cliente"] = adress_street

            poblacion = direccion_match.group("localidad")
            if "población_cliente" not in invoices:
                invoices["población_cliente"] = [poblacion]
                
            elif len(poblacion) < len(invoices["población_cliente"][0]):
                invoices["población_cliente"] = [poblacion]

            if "provincia_cliente" not in invoices:
                adress_province.append(direccion_match.group("provincia"))
                invoices["provincia_cliente"] = adress_province

        patron_adress_3 = r"calle\s+(?P<calle>.+?)\s+(\d{5})\s+(?P<localidad>.+?)\s+forma\s+de\s+pago\s+domiciliada"
        adress_3 = re.search(patron_adress_3, content)
        if adress_3:
            if "calle_cliente" not in invoices:
                adress_street.append("calle" + adress_3.group("calle"))
                invoices["calle_cliente"] = adress_street
            if "cp_cliente" not in invoices:
                adress_cp.append(adress_3.group(2))
                invoices["cp_cliente"] = adress_cp
            if "población_cliente" not in invoices:
                adress_city.append(adress_3.group("localidad"))
                invoices["población_cliente"] = adress_city
            # Patrón para encontrar el código postal entre la calle y la localidad
            if (n_pages >= 1):
                # Looking for cp from street
                found_street = adress_3.group("calle")
                found_city = adress_3.group("localidad")
                # Crear un patrón que busque el código postal entre la calle y la localidad
                patron_cp = fr'{re.escape(found_street)}\s+(\d{{5}})\s+{re.escape(found_city)}'
                cp_match = re.search(patron_cp, content)

                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp
            if (invoices["nombre_cliente"]):
                found_client_name = invoices["nombre_cliente"][0]  # Suponiendo que solo hay un nombre almacenado en la lista
                # Patrón para encontrar el código postal después del nombre del cliente
                patron_cp = fr'{re.escape(found_client_name)}.*?(\d{{5}})'
                cp_match = re.search(patron_cp, pages[n_pages])
                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp

        patron_adress_4 = r"direccion\sde\ssuministro\s(?P<calle>.+?)\s+(?P<codigo_postal>\d{5})\s+(?P<localidad>\w+)"
        adress_4 = re.search(patron_adress_4, content)
        if adress_4:
            if "calle_cliente" not in invoices:
                adress_street.append(adress_4.group("calle"))
                invoices["calle_cliente"] = adress_street
            if "cp_cliente" not in invoices:
                adress_cp.append(adress_4.group("codigo_postal"))
                invoices["cp_cliente"] = adress_cp
            if "población_cliente" not in invoices:
                adress_city.append(adress_4.group("localidad"))
                invoices["población_cliente"] = adress_city

            # Patrón para encontrar el código postal entre la calle y la localidad
            if (n_pages >= 1):
                # Looking for cp from street
                found_street = adress_4.group("calle")
                found_city = adress_4.group("localidad")
                # Crear un patrón que busque el código postal entre la calle y la localidad
                patron_cp = fr'{re.escape(found_street)}\s+(\d{{5}})\s+{re.escape(found_city)}'
                cp_match = re.search(patron_cp, pages[n_pages - 1])

                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp[0]
            if (invoices["nombre_cliente"]):
                found_client_name = invoices["nombre_cliente"][0]  # Suponiendo que solo hay un nombre almacenado en la lista
                # Patrón para encontrar el código postal después del nombre del cliente
                patron_cp = fr'{re.escape(found_client_name)}.*?(\d{{5}})'
                cp_match = re.search(patron_cp, pages[n_pages])
                if cp_match:
                    if "cp_cliente" not in invoices:
                        adress_cp.append(cp_match.group(1))
                        invoices["cp_cliente"] = adress_cp
        
        #----------------------------------------------------------------------------------------------
        # CIF de la empresa comercializadora
        patron_cif_1 = r"cif\s+(?P<cif>[a-zA-Z]\d{8})\."
        cif_match = re.search(patron_cif_1, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif
        # CIF de la empresa comercializadora
        patron_cif_2 = r"cif\s+(?P<cif>[a-zA-Z]\d{8})\s*\."
        cif_match = re.search(patron_cif_2, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif
        
        # CIF de la empresa comercializadora
        patron_cif_3 = r"cif\s+(?P<cif>[a-zA-Z]\d{8})\b"
        cif_match = re.search(patron_cif_3, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif

        # CIF de la empresa comercializadora
        patron_cif_4 = r"cif\s+(?P<cif>[a-zA-Z]{1,2}\d{6,8})\s*\."
        cif_match = re.search(patron_cif_4, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif

        # CIF de la empresa comercializadora
        patron_cif_5 = r"cif\s+(?P<cif>[a-zA-Z]{1,2}\d{6,8})\b"
        cif_match = re.search(patron_cif_5, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif

        patron_cif_6 = r"cif\s+(?P<cif>[a-zA-Z]{1,2}\d{6,9})\b"
        cif_match = re.search(patron_cif_6, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif

        # CIF de la empresa comercializadora
        patron_cif_1 = r"cif\s+(?P<cif>[a-zA-Z]{1,3}\s?\d{3}(\.?\d{3}){1,2}|\d{3}'\d{3}|\d{9,10})[\s\.]*"
        cif_match = re.search(patron_cif_1, pages[n_pages])

        if cif_match:
            if "cif_comercializadora" not in invoices:
                cif.append(cif_match.group("cif"))
                invoices["cif_comercializadora"] = cif

        #-----------------------------------------------------------------------------------------------
        # Dirección de la empresa 
        if (invoices['nombre_cliente']):
            if ("cif_comercializadora" in invoices):
                patron_location_1 = r"(?P<nombre_empresa>[^\d.]+)\s*\. cif\s*{}\s*\.\s*(?P<direccion>.*?)\s*(?P<cp>\d{{5}})\s*(?P<localidad>[^\s]*).*{}".format(invoices["cif_comercializadora"][0], re.escape(invoices["nombre_cliente"][0]))
                if (n_pages >= 1):
                    location_match = re.search(patron_location_1, pages[n_pages - 1], re.IGNORECASE)
                else:
                    location_match = re.search(patron_location_1, pages[n_pages], re.IGNORECASE)

                if location_match:
                
                    if "nombre_comercializadora" not in invoices:
                        distributor_name.append(location_match.group('nombre_empresa'))
                        invoices["nombre_comercializadora"] = distributor_name
    
                    if "dirección_comercializadora" not in invoices:
                        distributor_street.append(location_match.group('direccion').strip())
                        invoices["dirección_comercializadora"] = distributor_street
    
                    if "cp_comercializadora" not in invoices:
                        distributor_cp.append(location_match.group('cp'))
                        invoices["cp_comercializadora"] = distributor_cp
    
                    if "localidad_comercializadora" not in invoices:
                        distributor_city.append(location_match.group('localidad'))
                        invoices["localidad_comercializadora"] = distributor_city

                patron_location_2 = r"fecha de cargo.*?(?P<nombre_empresa>[^\d]+?)\s+cif\s+{}\s+(?P<direccion>.*?)\s+(?P<cp>\d{{5}})\s+(?P<localidad>[^\s]+)\s+{}".format(invoices["cif_comercializadora"][0], re.escape(invoices["nombre_cliente"][0]))
                if (n_pages >= 1):
                    location_match = re.search(patron_location_2, pages[n_pages - 1], re.IGNORECASE)
                else:
                    location_match = re.search(patron_location_2, pages[n_pages], re.IGNORECASE)

                if location_match:
                
                    if "nombre_comercializadora" not in invoices:
                        distributor_name.append(location_match.group('nombre_empresa'))
                        invoices["nombre_comercializadora"] = distributor_name
    
                    if "dirección_comercializadora" not in invoices:
                        distributor_street.append(location_match.group('direccion').strip())
                        invoices["dirección_comercializadora"] = distributor_street
    
                    if "cp_comercializadora" not in invoices:
                        distributor_cp.append(location_match.group('cp'))
                        invoices["cp_comercializadora"] = distributor_cp
    
                    if "localidad_comercializadora" not in invoices:
                        distributor_city.append(location_match.group('localidad'))
                        invoices["localidad_comercializadora"] = distributor_city

        patron_location_3 = r"(?<=mifactura\s)(?P<nombre_empresa>[A-Za-z\s,\.]+?)\s*\.?\s*dom\. social\s+(?P<direccion>.*?),\s*(?P<cp>\d{5})\s+(?P<localidad>[^\.\,]+)\.\s*(?P<provincia>[^\.\,]+)"
        location_match = re.search(patron_location_3, pages[n_pages], re.IGNORECASE)

        if location_match:
        
            if "nombre_comercializadora" not in invoices:
                distributor_name.append(location_match.group('nombre_empresa'))
                invoices["nombre_comercializadora"] = distributor_name

            if "dirección_comercializadora" not in invoices:
                distributor_street.append(location_match.group('direccion').strip())
                invoices["dirección_comercializadora"] = distributor_street

            if "cp_comercializadora" not in invoices:
                distributor_cp.append(location_match.group('cp'))
                invoices["cp_comercializadora"] = distributor_cp

            if "localidad_comercializadora" not in invoices:
                distributor_city.append(location_match.group('localidad'))
                invoices["localidad_comercializadora"] = distributor_city

            if "provincia_comercializadora" not in invoices:
                distributor_province.append(location_match.group('provincia'))
                invoices["provincia_comercializadora"] = distributor_province

        if ("cif_comercializadora" in invoices):
            patron_location_4 = r"(?P<nombre_empresa>[^\d]+?)\s+cif\s+{}\s+(?P<direccion>.*?)\s+(?P<cp>\d{{5}})\s+(?P<localidad>[^\s]+)".format(re.escape(invoices["cif_comercializadora"][0]))
            if (n_pages >= 1):
                location_match = re.search(patron_location_4, pages[n_pages - 1], re.IGNORECASE)
            else:
                location_match = re.search(patron_location_4, pages[n_pages], re.IGNORECASE)

            if location_match:
            
                if "nombre_comercializadora" not in invoices:
                    distributor_name.append(location_match.group('nombre_empresa'))
                    invoices["nombre_comercializadora"] = distributor_name

                if "dirección_comercializadora" not in invoices:
                    distributor_street.append(location_match.group('direccion').strip())
                    invoices["dirección_comercializadora"] = distributor_street

                if "cp_comercializadora" not in invoices:
                    distributor_cp.append(location_match.group('cp'))
                    invoices["cp_comercializadora"] = distributor_cp

                if "localidad_comercializadora" not in invoices:
                    distributor_city.append(location_match.group('localidad'))
                    invoices["localidad_comercializadora"] = distributor_city

        patron_location_5 =  r"\/mifactura\s+(?P<nombre_empresa>.*?)\.\s+dom\.?\s+social\s+(?P<direccion>.*?)\,\s+(?P<cp>\d{4})\s+(?P<localidad>[\w\s]+)\.\s+(?P<provincia>[\w\s]+),"
        location_match = re.search(patron_location_5, pages[n_pages], re.IGNORECASE)

        if location_match:
        
            if "nombre_comercializadora" not in invoices:
                distributor_name.append(location_match.group('nombre_empresa'))
                invoices["nombre_comercializadora"] = distributor_name

            if "dirección_comercializadora" not in invoices:
                distributor_street.append(location_match.group('direccion').strip())
                invoices["dirección_comercializadora"] = distributor_street

            if "provincia_comercializadora" not in invoices:
                distributor_province.append(location_match.group('provincia'))
                invoices["provincia_comercializadora"] = distributor_province
        
        patron_location_6 = r"domicilio\s+social\s+(?P<direccion>[^,]+),\s*(?P<localidad>[^\.,]+) xxxxx"
        location_match = re.search(patron_location_6, pages[n_pages])

        if location_match:
            
            if "dirección_comercializadora" not in invoices:
                distributor_street.append(location_match.group('direccion').strip())
                invoices["dirección_comercializadora"] = distributor_street
            if "localidad_comercializadora" not in invoices:
                distributor_city.append(location_match.group('localidad').strip())
                invoices["localidad_comercializadora"] = distributor_city

        # --------------------------------------------------------------------------------------------
        # Nombre de la comercializadora
        patron_name_1 = r"[\s.]+(?P<nombre_empresa>[^\.,]+)\.\s+inscrita"
        name_match = re.search(patron_name_1, pages[n_pages])

        if name_match:
            if "nombre_comercializadora" not in invoices:
                distributor_name.append(name_match.group('nombre_empresa'))
                invoices["nombre_comercializadora"] = distributor_name

        # ----------------------------------------------------------------------------------------------
        # Patrón para el importe de la factura
        importe_pattern = r"importe factura (\d{1,3}(?:\.\d{3})*(?:,\d{2})?)"
        # Patrón para el número de factura
        invoice_number_pattern = r"no factura (\w+)"
        # Patrón para las fechas de inicio y final de facturación
        dates_pattern = r"periodo de consumo (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})"
        # Patrón para la fecha de cargo
        cargo_date_pattern = r"fecha de cargo (\d{1,2} de \w+ de \d{4})"

         # Inicializar las variables
        importe = None
        invoice_number = None
        start_date = None
        end_date = None
        cargo_date = None

        # Buscar los patrones en el texto
        importe_match = re.search(importe_pattern, pages[n_pages])
        if importe_match:
            if ("importe_factura" not in invoices):
                importe = importe_match.group(1)
                invoices["importe_factura"] = importe
            
        invoice_number_match = re.search(invoice_number_pattern, pages[n_pages])
        if invoice_number_match:
            if ("número_factura" not in invoices):
                invoice_number = invoice_number_match.group(1)
                invoices["número_factura"] = invoice_number
        
        dates_match = re.search(dates_pattern, pages[n_pages])
        if dates_match:
            if ("inicio_periodo" not in invoices):
                start_date = dates_match.group(1)
                invoices["inicio_periodo"] = start_date
            if ("fin_periodo" not in invoices):
                end_date = dates_match.group(2)
                invoices["fin_periodo"] = end_date

        dates_pattern = r"del (\d{2}\.\d{2}\.\d{4}) al (\d{2}\.\d{2}\.\d{4})"
        # Buscar el patrón en el texto
        dates_match = re.search(dates_pattern, pages[n_pages])
        if dates_match:
            if ("inicio_periodo" not in invoices):
                start_date = dates_match.group(1)
                invoices["inicio_periodo"] = start_date
            if ("fin_periodo" not in invoices):
                end_date = dates_match.group(2)
                invoices["fin_periodo"] = end_date
        
        dates_pattern = r"periodo de facturacion del (\d{2}/\d{2}/\d{4}) a (\d{2}/\d{2}/\d{4})"
        dates_match = re.search(dates_pattern, pages[n_pages])
        if dates_match:
            if ("inicio_periodo" not in invoices):
                start_date = dates_match.group(1)
                invoices["inicio_periodo"] = start_date
            if ("fin_periodo" not in invoices):
                end_date = dates_match.group(2)
                invoices["fin_periodo"] = end_date
        
        dates_pattern = r"periodo de consumo (\d{1,2} de \w+ de \d{4}) a (\d{1,2} de \w+ de \d{4})"
        dates_match = re.search(dates_pattern, pages[n_pages])
        if dates_match:
            if ("inicio_periodo" not in invoices):
                start_date = dates_match.group(1)
                invoices["inicio_periodo"] = start_date
            if ("fin_periodo" not in invoices):
                end_date = dates_match.group(2)
                invoices["fin_periodo"] = end_date
        
        cargo_date_match = re.search(cargo_date_pattern, pages[n_pages])
        if cargo_date_match:
            if ("fecha_cargo" not in invoices):
                cargo_date = cargo_date_match.group(1)
                invoices["fecha_cargo"] = cargo_date
        
        cargo_date_pattern = r"fecha de cargo (\d{2}\.\d{2}\.\d{4})"
        cargo_date_match = re.search(cargo_date_pattern, pages[n_pages])
        if cargo_date_match:
            if ("fecha_cargo" not in invoices):
                cargo_date = cargo_date_match.group(1)
                invoices["fecha_cargo"] = cargo_date

        amount_pattern = r"importe de su factura, (\d+(?:,\d+)*(?:\.\d{2})?) euros"
        # Inicializar la variable
        invoice_amount = None
        # Buscar el patrón en el texto
        amount_match = re.search(amount_pattern, pages[n_pages])
        if amount_match:
            if ("importe_factura" not in invoices):
                invoice_amount = amount_match.group(1)
                invoices["importe_factura"] = invoice_amount

        # Patrón para el periodo de facturación seguido del consumo en kWh
        consumption_pattern = r"periodo de \d{2}\.\d{2}\.\d{4} a \d{2}\.\d{2}\.\d{4} (\d+) kwh \d+ dias"
        # Inicializar la variable
        consumption = None
        # Buscar el patrón en el texto
        consumption_match = re.search(consumption_pattern, pages[n_pages])
        if consumption_match:
            if ("consumo_periodo" not in invoices):
                consumption = consumption_match.group(1)
                invoices["consumo_periodo"] = consumption
        
        consumption_pattern = r"periodo de \d{2}\.\d{2}\.\d{4} a \d{2}\.\d{2}\.\d{4} (\d+) kwh"
        # Buscar el patrón en el texto
        consumption_match = re.search(consumption_pattern, pages[n_pages])
        if consumption_match:
            if ("consumo_periodo" not in invoices):
                consumption = consumption_match.group(1)
                invoices["consumo_periodo"] = consumption

        consumption_pattern = r"importe por energia consumida (\d+) kwh"
        # Buscar el patrón en el texto
        consumption_match = re.search(consumption_pattern, pages[n_pages])
        if consumption_match:
            consumption = int(consumption_match.group(1))
            if ("consumo_periodo" not in invoices):
                invoices["consumo_periodo"] = consumption

        consumption_pattern = r"consumo en el periodo (\d+) kwh"
        # Buscar el patrón en el texto
        consumption_match = re.search(consumption_pattern, pages[n_pages])
        if consumption_match:
            consumption = int(consumption_match.group(1))
            if ("consumo_periodo" not in invoices):
                invoices["consumo_periodo"] = consumption

        consumption_pattern = r"importe por peaje de acceso (\d+) kwh"
        # Buscar el patrón en el texto
        consumption_match = re.search(consumption_pattern, pages[n_pages])
        if consumption_match:
            consumption = int(consumption_match.group(1))
            if ("consumo_periodo" not in invoices):
                invoices["consumo_periodo"] = consumption

        power_pattern = r"potencia contratada ([\d,]+) kw"
        # Inicializar la variable
        power = None
        # Buscar el patrón en el texto
        power_match = re.search(power_pattern, pages[n_pages])
        if power_match:
            if "potencia_contratada" not in invoices:
                # Reemplazar la coma por un punto para asegurar el formato float
                power = power_match.group(1)
                invoices["potencia_contratada"] = power
          
    if (len(adress_province) == 0):
        adress_province = [encontrar_provincia_por_cp(invoices["cp_cliente"][0], "ES")]
        invoices["provincia_cliente"] = adress_province

    if (len(distributor_province) == 0):
        if ("cp_comercializadora" in invoices):
            adress_province = [encontrar_provincia_por_cp(invoices["cp_comercializadora"][0], "ES")]
            invoices["provincia_comercializadora"] = adress_province

    # Fill result
    result[name] = invoices

    
    return result

def ft_date_convert(date):
    meses = {
        'enero': 'January',
        'febrero': 'February',
        'marzo': 'March',
        'abril': 'April',
        'mayo': 'May',
        'junio': 'June',
        'julio': 'July',
        'agosto': 'August',
        'septiembre': 'September',
        'octubre': 'October',
        'noviembre': 'November',
        'diciembre': 'December'
    }
    try:
        # Convertir la cadena de fecha a minúsculas para manejar diferentes casos
        date = date.lower()
        
        # Traducir los nombres de los meses a inglés
        for mes_es, mes_en in meses.items():
            date = date.replace(mes_es, mes_en)
        
        # Probar diferentes formatos de fecha
        if 'de' in date:
            date = datetime.strptime(date, '%d %B %Y')
        elif '.' in date:
            date = datetime.strptime(date, '%d.%m.%Y')
        else:
            date = datetime.strptime(date, '%d/%m/%Y')
            
        date = date.strftime("%m.%d.%Y")
    except ValueError:
        # Manejar errores de conversión de fecha
        print("Error: Formato de fecha incorrecto.")
    
    return date

def ft_solution(result, name):
    result = result[list(result.keys())[0]]
    
    for key, value in result.items():
        if key == "nombre_cliente":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "dni_cliente":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "calle_cliente":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "cp_cliente":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "población_cliente":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "provincia_cliente":
            try:
                result[key] = value[0]
            except:
                pass

        if key == "cif_comercializadora":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "nombre_comercializadora":
            try:
                result[key] = value[0].replace(".", "")
            except:
                pass
        if key == "dirección_comercializadora":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "cp_comercializadora":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "localidad_comercializadora":
            try:
                result[key] = value[0]
            except:
                pass
        if key == "provincia_comercializadora":
            try:
                result[key] = value[0]
            except:
                pass

        if key == "número_factura":
            try:
                result[key] = value
            except:
                pass
        if key == "inicio_periodo":
            try:
                result[key] = ft_date_convert(value)
            except:
                pass
        if key == "fin_periodo":
            try:
                result[key] = ft_date_convert(value)
            except:
                pass
        if key == "fecha_cargo":
            try:
                result[key] = ft_date_convert(value)
            except:
                pass
        if key == "importe_factura":
            try:
                result[key] = value
            except:
                pass
        if key == "consumo_periodo":
            try:
                result[key] = int(value.replace(",", ""))
            except:
                pass
        if key == "potencia_contratada":
            try:
                result[key] = value
            except:
                pass

        with open(f"{name}.json", "w") as archivo_json:
            json.dump(result, archivo_json)
    
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from a PDF invoice and save it as JSON.")
    parser.add_argument("pdf_path", help="Path to the PDF invoice file")
    args = parser.parse_args()

    pdf_path = args.pdf_path
    try:
        # Extraer el nombre del archivo sin la extensión
        name = os.path.splitext(os.path.basename(pdf_path))[0]
        factura = ft_readinvoice(pdf_path, name)
        factura_limpia = ft_normalize(name)
        result = ft_font_code(factura_limpia, name)
        new_result = ft_solution(result, name)
        print(new_result)
    except Exception as e:
        print(f"Ha fallado el procesamiento de la factura: {e}")