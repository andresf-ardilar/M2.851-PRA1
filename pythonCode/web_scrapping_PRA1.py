# from bs4 import BeautifulSoup
import numpy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime

import re


# Se inicializan las variables globales y el driver de selenium con Firefox
def setup(url_to_scrap):
    global prices
    prices = []
    global prices_promo
    prices_promo = []
    global taxes
    taxes = []
    global data_in_gb
    data_in_gb = []
    global adquisition_types
    adquisition_types = []
    global benefits_all_text
    benefits_all_text = []
    global benefits_services
    benefits_services = []
    global benefits_types
    benefits_types = []
    global offer_date
    offer_date = []
    global company
    company = []

    global driver
    driver = webdriver.Firefox()
    driver.get(url_to_scrap)


# Método principal que extrae el HTML con Selenium y se procesa iterando sobre la estructura HTML
def scrap_data_tigo():
    # Lista de servicios para dividir el texto extraído
    benefits_service_list = ['Facebook', 'WhatsApp', 'Instagram', 'Amazon Music', 'Amazon Prime Video', 'Deezer',
                             'Servicio preferencial', 'Voz', 'SMS', 'EEUU', 'Canadá', 'Puerto Rico']

    # Lista de tipos para dividir el texto extraído
    benefits_types_list = ['sin consumir datos', 'Llamadas ilimitadas', 'ilimitados']

    # Se invoca un click para extender los beneficios. Se buscan todos los elementos con clase
    # "btn-show-more-benefits-pospago"
    benefits_button = driver.find_elements(by=By.CLASS_NAME, value="btn-show-more-benefits-pospago")
    print('benefitsButton: ', len(benefits_button))
    for benefits_by_plan in benefits_button:
        try:
            # Si el elemento es visible se despliega. Se aplica esta validación para evitar errores cuando Selenium
            # hace click sobre un objeto oculto
            if benefits_by_plan.is_displayed():
                print("click")
                # Se hace click sobre el boton para desplegar la lista completa de beneficios
                benefits_by_plan.click()
        except Exception:
            pass

    # Se obtienen todos los elementos con clase "Article". Estos elementos corresponden a los 5 planes visibles en la
    # página
    plans_list = driver.find_elements(by=By.CSS_SELECTOR, value=".list_cards article")
    print('plansList:', len(plans_list))

    # Se itera plan a plan para obtener toda la información, procesarla, limpiarla y guardarla en sus respectivos
    # arreglos
    for plan_card in plans_list:
        if plan_card.is_displayed():
            # Se obtienen la lista de beneficios buscando todos los nodos de tipo "p" dentro de una lista "ul"
            benefit_list = plan_card.find_elements(by=By.TAG_NAME, value="ul p")
            print('benefit list:', len(benefit_list))

            # Se itera beneficio a para extraer la información importante
            for benefit in benefit_list:
                print('taxes:', plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())
                # Se extrae el impuesto del plan y se agrega al arreglo correspondiente
                taxes.append(plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())

                print('price:', plan_card.find_element(by=By.CLASS_NAME, value="price").text.strip())
                # Se extrae el precio del plan y se agrega al arreglo correspondiente
                prices.append(plan_card.find_element(by=By.CLASS_NAME, value="price").text.strip() + ".000")

                # Se extraen los GB de navegación incluidos en el plan y se agrega al arreglo correspondiente
                print('gb:', plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text.strip())
                data_in_gb.append(plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text.strip())

                # Se extraen el texto del beneficio sin procesar del plan y se agrega al arreglo correspondiente
                print(' benefit:', benefit.text.strip())
                benefits_all_text.append(benefit.text.strip())

                # Se verifica si el servicio se encuentra en el arreglo con los valores predeterminados
                benefit_services_final = ""
                for benefit_service in benefits_service_list:
                    print("     benefit_service:", benefit_service)
                    # Si el beneficio de la lista predeterminada corresponde con el beneficio extraído se guardar
                    # en el arreglo y se separan los valores con coma
                    if benefit_service in benefit.text:
                        benefit_services_final += benefit_service + ','

                # Se extraen los valores del servicio cuando es tethering mediante una expresión regular y se cortan los
                # espacios al inicio y final con la función strip()
                is_tethering_service = re.findall(r"\d+GB.+Internet", benefit.text.strip())
                if is_tethering_service:
                    # Se agrega al arreglo el valor de los GB de tethering
                    benefit_services_final += re.findall(r"\d+GB", benefit.text.strip())[0]

                # Se extraen los valores del servicio cuando es roaming mediante una expresión regular y se cortan los
                # espacios al inicio y final con la función strip()
                is_roaming_service = re.findall(r"\d+GB.+Roaming", benefit.text.strip())
                if is_roaming_service:
                    # Se agrega al arreglo el valor de los GB de roaming
                    benefit_services_final += re.findall(r"\d+GB", benefit.text.strip())[0]

                # Se agrega al arreglo final la lista de servicios procesada
                benefits_services.append(benefit_services_final)
                print("         benefit_services_final:", benefit_services_final)

                # Se verifica si el tipo de servicio se encuentra en el arreglo con los valores predeterminados
                benefit_types_final = ""
                for benefit_type in benefits_types_list:
                    print("     benefit_type:", benefit_type)
                    # Si el tipo de beneficio de la lista predeterminada corresponde con el beneficio extraído se
                    # guarda en el arreglo y se separan los valores con coma
                    if benefit_type in benefit.text:
                        benefit_types_final += benefit_type + ','

                # Se extraen los valores del servicio cuando es servicio de cortesía mediante una expresión regular y
                # se cortan los espacios al inicio y final con la función strip()
                is_courtesy_service = re.findall(r"\d+.mes.+de.+cortesía", benefit.text.strip())
                if is_courtesy_service:
                    # Se agrega al arreglo los meses de cortesía
                    benefit_types_final += re.findall(r"\d+.mes.+de.+cortesía", benefit.text.strip())[0]

                # Se agrega al arreglo final la lista de tipos procesada
                benefits_types.append(benefit_types_final)
                print("         benefit_types_final:", benefit_types_final)

                # Se extraen los tipos de adquisición de cada plan mediante clase
                buy_options_list = plan_card.find_elements(by=By.CLASS_NAME, value="buy-option")

                buy_options_final = ""
                for buy_option in buy_options_list:
                    # Se obtiene el texto de cada opción de compra
                    print('buy_option:', buy_option.get_attribute('text'))
                    # Se agrega al arreglo las opciones de compra o tipos de adquisición separados por coma
                    buy_options_final += buy_option.get_attribute('text') + ','

                # Se agrega al arreglo final la lista de opciones de compra
                adquisition_types.append(buy_options_final)
                print("         buy_option_final:", buy_options_final)

                # Se establece la fecha de captura de datos (fecha en que corre el script)
                offer_date.append(datetime.datetime.now(datetime.timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"))

                # se agrega info de la empresa
                company.append("Tigo")

    # Se imprimen los arreglos para verificar que coincidan los tamaños de cada uno y sus respectivos valores
    print("prices:", len(prices), prices)
    print("taxes:", len(taxes), taxes)
    print("data_in_gb:", len(data_in_gb), data_in_gb)
    print("benefits_all_text:", len(benefits_all_text), benefits_all_text)
    print("benefits_services:", len(benefits_services), benefits_services)
    print("benefits_types:", len(benefits_types), benefits_types)
    print("adquisition_types:", len(adquisition_types), adquisition_types)
    print("offer_date:", len(offer_date), offer_date)

    # Se cierra el driver de selenium (cierra el navegador)
    driver.quit()


# Método principal que extrae el HTML con Selenium y se procesa iterando sobre la estructura HTML
def scrap_data_movistar():
    # Lista de servicios para dividir el texto extraído
    benefits_service_list = ['Facebook', 'WhatsApp', 'Instagram', 'Amazon Music', 'Amazon Prime Video', 'Deezer',
                             'Servicio preferencial', 'Voz', 'SMS', 'EEUU', 'Canadá', 'Puerto Rico',
                             'Estados Unidos', 'Waze', 'Twitter', 'TikTok', 'Venezuela', 'Cloud', 'América Latina',
                             'España']

    # Lista de tipos para dividir el texto extraído
    benefits_types_list = ['sin consumir datos', 'Llamadas ilimitadas', 'ilimitados', 'ilimitadas', 'minutos',
                           'Ilimitados', 'Minutos', 'Apps ilimitadas']

    # Se cambia el display none por display block para ver los beneficios por plan. Se buscan todos los elementos con
    # clase "plan__content"
    plan_benefits_display = driver.find_elements(by=By.CLASS_NAME, value="plan__content")
    for plan_benefit_display in plan_benefits_display:
        try:
            driver.execute_script("arguments[0].style.display = 'block';", plan_benefit_display)
        except Exception:
            pass

    # Se obtienen todos los elementos con clase ".tab_CambiateAMovistar .plan__container".
    # Estos elementos corresponden a los planes visibles en la página
    plans_list = driver.find_elements(by=By.CSS_SELECTOR,
                                      value=".tab_CambiateAMovistar .plan__container")
    print('plans_list:', len(plans_list))

    # Se itera plan a plan para obtener toda la información, procesarla, limpiarla y guardarla en sus respectivos
    # arreglos
    for plan_card in plans_list:

        benefits_list = plan_card.find_elements(by=By.CLASS_NAME, value="plan__item")

        # Se itera sobre cada uno de los beneficios para extraer la info relacionada
        for benefit in benefits_list:
            # Se obtienen los GB. Se valida mediante try catch si el nodo existe o no, dado que la estructura HTML
            # no es uniforme. Se guarda en el respectivo arreglo
            try:
                gb = plan_card.find_element(by=By.CLASS_NAME, value="cantidad"). \
                         get_attribute('innerHTML').strip() + "GB"
            except Exception:
                gb = "ILIMITADO"
            finally:
                print(' data:', gb)
                data_in_gb.append(gb)

            # Se obtiene el precio promocional. Se valida mediante try catch si el nodo existe o no, dado que la
            # estructura HTML no es uniforme. Se guarda en el respectivo arreglo
            try:
                price_promo = plan_card.find_element(by=By.CSS_SELECTOR, value=".plan-body__price .valueBody") \
                    .get_attribute('innerHTML').strip()
            except Exception:
                price_promo = "00"
            finally:
                print(' price_promo:', price_promo)
                prices_promo.append(price_promo + "COP")

            # Se obtiene el precio. Se valida mediante try catch si el nodo existe o no, dado que la
            # estructura HTML no es uniforme. Se guarda en el respectivo arreglo
            try:
                price = plan_card.find_element(by=By.CSS_SELECTOR, value=".plan-body__price .subPrice_body") \
                    .get_attribute('innerHTML').strip()
            except Exception:
                price = ""
            finally:
                print(' price:', price)
                prices.append(price)

            # Se obtiene el texto del beneficio sin procesar
            benefit_inner = remove_tags(
                benefit.find_element(by=By.CLASS_NAME, value="plan__item-text").get_attribute("innerHTML")) \
                .strip()
            print('     benefits_text:', benefit_inner)
            benefits_all_text.append(benefit_inner)

            # Se verifica si el servicio se encuentra en el arreglo con los valores predeterminados
            benefit_services_final = ""
            for benefit_service in benefits_service_list:
                # Si el beneficio de la lista predeterminada corresponde con el beneficio extraído se guardar
                # en el arreglo y se separan los valores con coma
                if benefit_service in benefit_inner:
                    print("         benefit_service:", benefit_service)
                    benefit_services_final += benefit_service + ','

            # Se extraen los valores del servicio cuando es tethering mediante una expresión regular y se cortan los
            # espacios al inicio y final con la función strip()
            is_tethering_service = re.findall(r"s.+\d", benefit_inner)
            if is_tethering_service:
                # Se agrega al arreglo el valor de los GB de tethering
                print("         tethering:", is_tethering_service)
                benefit_services_final += re.findall(r"\d+", benefit_inner)[0]

            # Se extraen los valores del servicio cuando es roaming mediante una expresión regular y se cortan los
            # espacios al inicio y final con la función strip()
            is_roaming_service = re.findall(r"s.+\d.+GB.+para.+Roaming", benefit_inner)
            if is_roaming_service:
                # Se agrega al arreglo el valor de los GB de roaming
                benefit_services_final += re.findall(r"\d+", benefit_inner)[0]

            # Se extraen los valores del servicio cuando son minutos internacionales mediante una expresión regular
            # y se cortan los espacios al inicio y final con la función strip()
            is_international_service = re.findall(r"\d.+minutos", benefit_inner)
            if is_international_service:
                # Se agrega al arreglo el valor de los GB de roaming
                benefit_services_final += re.findall(r"\d+", benefit_inner)[0]

            # Se agrega al arreglo final la lista de servicios procesada
            benefits_services.append(benefit_services_final)
            print("             benefit_services_final:", benefit_services_final)

            # Se verifica si el tipo de servicio se encuentra en el arreglo con los valores predeterminados
            benefit_types_final = ""
            for benefit_type in benefits_types_list:
                print("         benefit_type:", benefit_type)
                # Si el tipo de beneficio de la lista predeterminada corresponde con el beneficio extraído se
                # guarda en el arreglo y se separan los valores con coma
                if benefit_type in benefit_inner:
                    benefit_types_final += benefit_type + ','
            # Se agrega al arreglo final la lista de tipos procesada
            benefits_types.append(benefit_types_final)
            print("             benefit_types_final:", benefit_types_final)

            # Se extraen los tipos de adquisición de cada plan mediante la clase .pospago__tablink
            buy_options_list = driver.find_elements(by=By.CLASS_NAME, value="pospago__tablink")
            buy_options_final = ""
            for buy_option in buy_options_list:
                # Se obtiene el texto de cada opción de compra
                print('     buy_option:', buy_option.get_attribute('text'))
                # Se agrega al arreglo las opciones de compra o tipos de adquisición separados por coma
                buy_options_final += buy_option.get_attribute('text') + ','

            # Se agrega al arreglo final la lista de opciones de compra
            adquisition_types.append(buy_options_final)

            # Se establece la fecha de captura de datos (fecha en que corre el script)
            offer_date.append(datetime.datetime.now(datetime.timezone.utc).strftime("%m/%d/%Y, %H:%M:%S"))

            # Se agrega info de impuestos
            taxes.append("")

            # se agrega info de la empresa
            company.append("Movistar")

    print("data_in_gb:", len(data_in_gb), data_in_gb)
    print("prices:", len(prices), prices)
    print("prices_promo:", len(prices_promo), prices_promo)
    print("benefits_all_text:", len(benefits_all_text), benefits_all_text)
    print("benefits_services:", len(benefits_services), benefits_services)
    print("adquisition_types:", len(adquisition_types), adquisition_types)
    print("offer_date:", len(offer_date), offer_date)

    driver.quit()


# Se reemplazan valores extraídos por valores standarizados
def replace_values():
    # Se reemplaza valores de impuestos por valor standard
    index = 0
    for tax_text in taxes:
        taxes[index] = tax_text.replace("CARGO BÁSICO IVA incluido", "IVA incluido")
        index += 1
    print("taxes replaced:", len(taxes), taxes)

    # Se reemplaza valores de sin consumo de datos por valor standard
    index = 0
    for benefit_type in benefits_types:
        benefits_types[index] = benefit_type.replace("sin consumir datos", "0 rate")
        adquisition_types[index] = adquisition_types[index].replace("Apps ilimitadas", "0 rate")
        index += 1
    print("benefits_types replaced:", len(benefits_types), benefits_types)

    # Se reemplaza valores de tipos de adquisición por valor standard
    index = 0
    for adquisition_type in adquisition_types:
        adquisition_types[index] = adquisition_type.replace("Pasar mi número a Tigo", "portación")
        adquisition_types[index] = adquisition_types[index].replace("Comprar una línea Nueva", "línea nueva")
        adquisition_types[index] = adquisition_types[index].replace("Cambiarme de prepago a pospago", "pre2pos")
        adquisition_types[index] = adquisition_types[index].replace("Cámbiate a Movistar", "portación")
        adquisition_types[index] = adquisition_types[index].replace("Línea Nueva", "línea nueva")
        index += 1
    print("adquisition_types replaced:", len(adquisition_types), adquisition_types)

    # Se reemplaza los miles del precio, se elimina el sigo "$" y se agrega la moneda en formato ISO 4217
    index = 0
    for price in prices:
        prices[index] = price.replace("MIL", "")
        prices[index] = prices[index].replace("$", "")
        prices[index] = prices[index].replace("mes", "")
        prices[index] = prices[index].replace(" ", "")
        prices[index] = prices[index].replace("Normal:", "")
        prices[index] = prices[index] + "COP"
        index += 1
    print("prices replaced:", len(prices), prices)

    # Se reemplaza se elimina el sigo "$" y se agrega la moneda en formato ISO 4217 en el arreglo precio promo,
    index = 0
    for price_promo in prices_promo:
        prices_promo[index] = prices_promo[index].replace("$", "")
        index += 1
    print("prices promo replaced:", len(prices_promo), prices_promo)


# Se guardan los arreglos en un dataframe. Se exporta el dataframe a un csv
def save_data_to_csv():
    global prices_promo
    # Se modifica prices_promo si no tiene el mismo tamaño de los otros arreglos
    # La página de Tigo no tiene precios promocionales, p lo que es necesaria esta validación para reutilizar el método
    # en el web scrapping de ambos sitios web
    if len(prices_promo) == 0:
        prices_promo = numpy.tile("", (len(prices)))

    df = pd.DataFrame({'Price': prices, 'Price (promo)': prices_promo, 'Tax': taxes, 'Navigation data': data_in_gb,
                       'Benefits text': benefits_all_text, 'Benefits services': benefits_services,
                       'Benefits types': benefits_types, 'Adquisition types': adquisition_types,
                       'Offer date': offer_date, 'Company': company})

    df.to_csv('dataset/plans_ATL.csv', index=False, encoding='utf-8', mode='a', header=False)


# Elimina cualquier tag HTML de un string
def remove_tags(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub(' ', text)


# Se invoca cada una de las funciones para ejecutar el script completo
setup("https://compras.tigo.com.co/movil/pospago")
scrap_data_tigo()
replace_values()
save_data_to_csv()

setup("https://www.movistar.co/pospago")
scrap_data_movistar()
replace_values()
save_data_to_csv()
