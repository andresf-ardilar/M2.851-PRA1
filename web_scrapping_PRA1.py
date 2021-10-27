# from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

import re


def setup(url_to_scrap):
    global prices
    prices = []
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

    global driver
    driver = webdriver.Firefox()
    driver.get(url_to_scrap)


def save_data_to_csv():
    df = pd.DataFrame({'Price': prices, 'Taxes': taxes, 'Navigation data': data_in_gb,
                       'Benefits (ori. text)': benefits_all_text, 'Benefits (services)': benefits_services,
                       'Benefits (types)': benefits_types, 'Adquisition types': adquisition_types})

    df.to_csv('plans_ATL_TIGO.csv', index=False, encoding='utf-8')


def scrap_data():
    benefits_service_list = ['Facebook', 'WhatsApp', 'Instagram', 'Amazon Music', 'Amazon Prime Video', 'Deezer',
                             'Servicio preferencial', 'Voz', 'SMS', 'EEUU', 'Canadá', 'Puerto Rico']

    benefits_types_list = ['sin consumir datos', 'Llamadas ilimitadas', 'ilimitados']

    benefits_button = driver.find_elements(by=By.CLASS_NAME, value="btn-show-more-benefits-pospago")
    print('benefitsButton: ', len(benefits_button))
    for benefits_by_plan in benefits_button:
        try:
            if benefits_by_plan.is_displayed():
                print("click")
                benefits_by_plan.click()
        except Exception:
            pass

    plans_list = driver.find_elements(by=By.CSS_SELECTOR, value=".list_cards article")
    print('plansList:', len(plans_list))

    for plan_card in plans_list:
        if plan_card.is_displayed():
            benefit_list = plan_card.find_elements(by=By.TAG_NAME, value="ul p")
            print('benefit list:', len(benefit_list))

            for benefit in benefit_list:
                print('taxes:', plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())
                taxes.append(plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())
                print('price:', plan_card.find_element(by=By.CLASS_NAME, value="price").text.strip())
                prices.append(plan_card.find_element(by=By.CLASS_NAME, value="price").text.strip())
                print('gb:', plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text.strip())
                data_in_gb.append(plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text.strip())

                print(' benefit:', benefit.text.strip())
                benefits_all_text.append(benefit.text.strip())

                ###
                benefit_services_final = ""
                for benefit_service in benefits_service_list:
                    print("     benefit_service:", benefit_service)
                    if benefit_service in benefit.text:
                        benefit_services_final += benefit_service + ','

                isTetheringService = re.findall(r"\d+GB.+Internet", benefit.text.strip())
                if isTetheringService:
                    benefit_services_final += re.findall(r"\d+GB", benefit.text.strip())[0]

                isRoamingService = re.findall(r"\d+GB.+Roaming", benefit.text.strip())
                if isRoamingService:
                    benefit_services_final += re.findall(r"\d+GB", benefit.text.strip())[0]

                benefits_services.append(benefit_services_final)
                print("         benefit_services_final:", benefit_services_final)

                ###
                benefit_types_final = ""
                for benefit_type in benefits_types_list:
                    print("     benefit_type:", benefit_type)
                    if benefit_type in benefit.text:
                        benefit_types_final += benefit_type + ','

                isCourtesyService = re.findall(r"\d+.mes.+de.+cortesía", benefit.text.strip())
                if isCourtesyService:
                    benefit_types_final += re.findall(r"\d+.mes.+de.+cortesía", benefit.text.strip())[0]

                benefits_types.append(benefit_types_final)
                print("         benefit_types_final:", benefit_types_final)

                ###
                buy_options_list = plan_card.find_elements(by=By.CLASS_NAME, value="buy-option")

                buy_options_final = ""
                for buy_option in buy_options_list:
                    print('buy_option:', buy_option.get_attribute('text'))
                    buy_options_final += buy_option.get_attribute('text') + ','

                adquisition_types.append(buy_options_final)
                print("         buy_option_final:", buy_options_final)

    print("prices:", len(prices), prices)
    print("taxes:", len(taxes), taxes)
    print("data_in_gb:", len(data_in_gb), data_in_gb)
    print("benefits_all_text:", len(benefits_all_text), benefits_all_text)
    print("benefits_services:", len(benefits_services), benefits_services)
    print("benefits_types:", len(benefits_types), benefits_types)
    print("adquisition_types:", len(adquisition_types), adquisition_types)

    driver.quit()


def replace_values():
    index = 0
    for tax_text in taxes:
        taxes[index] = tax_text.replace("CARGO BÁSICO IVA incluido", "IVA incluido")
        index += 1
    print("taxes replaced:", len(taxes), taxes)

    index = 0
    for benefit_type in benefits_types:
        benefits_types[index] = benefit_type.replace("sin consumir datos", "0 rate")
        index += 1
    print("benefits_types replaced:", len(benefits_types), benefits_types)

    index = 0
    for adquisition_type in adquisition_types:
        adquisition_types[index] = adquisition_type.replace("Pasar mi número a Tigo", "portación")
        adquisition_types[index] = adquisition_types[index].replace("Comprar una línea Nueva", "línea nueva")
        adquisition_types[index] = adquisition_types[index].replace("Cambiarme de prepago a pospago", "pre2pos")

        index += 1
    print("adquisition_types replaced:", len(adquisition_types), adquisition_types)


setup("https://compras.tigo.com.co/movil/pospago")
scrap_data()
replace_values()
save_data_to_csv()
