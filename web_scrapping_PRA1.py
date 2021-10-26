# from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

import re

# WEB SCRAPPING FOR https://compras.tigo.com.co/movil/pospago
driver = webdriver.Firefox()
driver.get("https://compras.tigo.com.co/movil/pospago")

benefits_button = driver.find_elements(by=By.CLASS_NAME, value="btn-show-more-benefits-pospago")
print('benefitsButton: ', len(benefits_button))
for benefits_by_plan in benefits_button:
    # print("Value is: %s" % benefitsByPlan.get_attribute("data-gtm-productid"))
    try:
        if benefits_by_plan.is_displayed():
            print("click")
            benefits_by_plan.click()
    except Exception:
        pass

plans_list = driver.find_elements(by=By.CSS_SELECTOR, value=".list_cards article")
print('plansList:', len(plans_list))

prices = []
taxes = []
data_in_gb = []
benefits_all_text = []
benefits_services = []

benefits_service_list = ['Facebook', 'WhatsApp', 'Instagram', 'Amazon Music', 'Amazon Prime Video', 'Deezer',
                         'Servicio preferencial', 'Voz', 'SMS', 'EEUU', 'Canadá', 'Puerto Rico']

for plan_card in plans_list:
    # print("Value is: %s" % benefitsByPlan.get_attribute("data-gtm-productid"))
    if plan_card.is_displayed():
        print('gb: ', plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text)
        data_in_gb.append(plan_card.find_element(by=By.CLASS_NAME, value="text-gb").text.strip())
        print('price: ', plan_card.find_element(by=By.CLASS_NAME, value="price").text)
        prices.append(plan_card.find_element(by=By.CLASS_NAME, value="price").text.strip())
        print('taxes: ', plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())
        taxes.append(plan_card.find_element(by=By.CSS_SELECTOR, value=".content_price_plan p").text.strip())

        benefit_list = plan_card.find_elements(by=By.TAG_NAME, value="ul p")
        print('benefit list: ', len(benefit_list))
        for benefit in benefit_list:
            print(' benefit: ', benefit.text)
            benefits_all_text.append(benefit.text.strip())
            benefit_services_final = ""
            for benefit_type in benefits_service_list:
                print("     benefit_type:", benefit_type)
                if benefit_type in benefit.text:
                    benefit_services_final += benefit_type + ','

            isTetheringService = re.findall(r"\d+GB.+Internet", benefit.text)
            if isTetheringService:
                benefit_services_final += re.findall(r"\d+GB", benefit.text)[0]

            isRoamingService = re.findall(r"\d+GB.+Roaming", benefit.text)
            if isRoamingService:
                benefit_services_final += re.findall(r"\d+GB", benefit.text)[0]

            benefits_services.append(benefit_services_final)
            print("         benefit_services_final: ", benefit_services_final)

print("benefits", benefits_all_text)
print("benefits_type", benefits_services)
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# print(soup.prettify())
#
# soup.find_all('p')
# print(soup.find_all('p')[0].get_text())
#
# soup.find_all('p', class_='outer-text')
# soup.find_all(class_="outer-text")
# soup.find_all(id="first")
#
# soup.select("div p")

# df = pd.DataFrame({'Product Name':products,'Price':prices,'Rating':ratings})
# df.to_csv('products.csv', index=False, encoding='utf-8')

driver.quit()
