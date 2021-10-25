from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Firefox()
driver.get("https://dataquestio.github.io/web-scraping-pages/ids_and_classes.html")

soup = BeautifulSoup(driver.page_source, 'html.parser')
print(soup.prettify())

soup.find_all('p')
print(soup.find_all('p')[0].get_text())

soup.find_all('p', class_='outer-text')
soup.find_all(class_="outer-text")
soup.find_all(id="first")

soup.select("div p")

# df = pd.DataFrame({'Product Name':products,'Price':prices,'Rating':ratings})
# df.to_csv('products.csv', index=False, encoding='utf-8')

driver.quit()
