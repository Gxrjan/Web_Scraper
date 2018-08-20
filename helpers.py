import requests
import bs4
import sys
import webbrowser
import csv
import time
import os
from datetime import datetime
from classes import *


CREATION_DATA = list()


# Deprecated
class UniqueDict(dict):
	# dict без повторений в keys
	def __setitem__(self, key, item):
		if key not in self:
			dict.__setitem__(self, key, item)
		else:
			raise KeyError("Key already exists " + key)


# Deprecated
def from_url_to_name(url):
	# берет название из url
	user_input = sys.argv[1]
	user_input = user_input[8:]
	bits = user_input.split(".")
	file_name = bits[1] + ".html" if bits[0] == "www" else bits[0] + ".html"
	file_name = bits[1] + ".html" if bits[0] == "www" else bits[0] + ".html"


def list_to_dict(data):
	# конвертирует из листа в дикт
	products = dict()
	for i in range(len(data)):
		if len(data[i]) > 3:
			products[data[i][0]] = (data[i][1], data[i][2], data[i][3])
		else:
			products[data[i][0]] = (data[i][1], data[i][2])
	return products


def str_to_bool(str):
	return str == 'True'


def get_data_from_db():
	if db_exists():
		fileRead = open('brandshop.csv', newline='', encoding='utf8')
		reader = csv.reader(fileRead)
		db = list(reader)
		product_list = list()
		for d in db:
			product = Product(int(d[0]), d[1], str_to_bool(d[2]), int(d[3]), int(d[4]), d[5], d[6], d[7])
			product_list.append(product)
		return product_list


# Deprecated
def is_on_sale(prd):
	if len(prd) > 2:
		return True
	else:
		return False


def str_to_int(pri):
	price = pri.replace('р', '')
	price = price.replace(' ', '')
	return price


def db_exists():
	return os.path.isfile('brandshop.csv')


# Deprecated
def get_product_page(href, name):
	# скачивает стринцу товара
	res = requests.get(href, verify=False)
	res.raise_for_status()
	file = open("products/" + name + ".html", "wb")
	for chunk in res.iter_content(100000):
		file.write(chunk)


def has_further_page(soup):
	elem = soup.find('a', text="Далее")
	if elem is not None:
		return True
	else:
		return False


# Deprecated
def display_name_price(href):
	# отражает название и цену переходя по ссылке на страницу продукта
	file = open('brandshop.csv', "w", newline="")
	writer = csv.writer(file)
	res = requests.get(href, verify=False)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	product_name = soup.find("span", itemprop="name").text
	regular_price = soup.find("span", class_="regprice")
	sale_price = soup.find("span", class_="saleprice")
	print(product_name)
	if not sale_price:
		print("Скидок не обнаружено!")
		print("Цена: " + regular_price.text.strip())
		writer.writerow([product_name, regular_price])
	else:
		print("Есть скидки!")
		print("Цена без скидки: " + regular_price.text.strip())
		print("Цена со скидкой: " + sale_price.text.strip())
		writer.writerow([product_name, regular_price, sale_price])
	print("----------------------------------------------")


def save_updates(updates):
	with open('updates.csv', 'a', encoding='utf8', newline='') as w:
		writer = csv.writer(w)
		for s in range(len(updates)):
			writer.writerow([str(datetime.now()), updates[s]])


def display_updates(updates):
	if len(updates) == 0:
		print("Новостей нет")
	else:
		print("\nНовости:")
		for s in range(len(updates)):
			print('%s: %s' % (s + 1, updates[s]))


def create_db():
	links = get_all_brands_links()
	for link in links:
			get_page_data(link[0], link[1])
	dump_data_to_db_new(CREATION_DATA)


def get_page_data(href, brand):
	res = requests.get(href, verify=False)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	product_containers = soup.select('.product-container')
	for l in range(len(product_containers)):
		get_product_data(str(product_containers[l]), brand)
	if has_further_page(soup):
		href = soup.find("a", text="Далее").attrs['href']
		get_page_data(href, brand)
	else:
		return


def get_product_data(html, brand):
	soup = bs4.BeautifulSoup(html, "html.parser")
	product_name = soup.find("h2").text
	product_id = soup.find('div', class_='product').attrs['data-product-id']
	price_box = soup.find('div', class_="price price-box")
	href = soup.find('a').attrs['href']
	img_src = soup.find('img').attrs['src']
	if soup.find('div', class_='product outofstock'): # Надо проработать обработку продукта если он outofstock
		return

	if not price_box:
		product = Product(product_id, product_name, False, 0, 0, brand, href, img_src)
	else:
		price = price_box.text.strip()
		if price_box['data-sale'] == 'sale:true':
			prices = price.split("\n")
			current_price = str_to_int(prices[0])
			regular_price = str_to_int(prices[1])
			product = Product(
				product_id, product_name, True,
				current_price, regular_price, brand, href, img_src)
		else:
			price = str_to_int(price)
			product = Product(product_id, product_name, False, price, price, brand, href, img_src)
	if product not in CREATION_DATA:
		CREATION_DATA.append(product)


def get_all_brands_links():
	res = requests.get('https://brandshop.ru/brandlist/', verify=False)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, 'html.parser')
	brands = soup.find_all('li', class_='active')
	brand_names = list()
	for b in brands:
		brand_names.append(b.text)
	save_brand_list(brand_names)
	links = list()
	for b in brands:
		link = b.find('a')
		links.append([link.attrs['href'], b.text.strip()])
	return links


# Deprecated
def dump_data_to_db(data):
	with open('brandshop.csv', 'w', newline='', encoding='utf8') as outfile:
		w = csv.writer(outfile)
		for k, v in data.items():
			if is_on_sale(v):
				w.writerow([k, v[0], v[1], v[2]])
			else:
				w.writerow([k, v[0], v[1]])


def dump_data_to_db_new(data):
	data.sort(key=lambda product: product.product_name.lower())
	with open('brandshop.csv', 'w', newline='', encoding='utf8') as outfile:
		writer = csv.writer(outfile)
		for p in data:
			writer.writerow([
				p.product_id, p.product_name,
				p.is_on_sale, p.current_price, p.regular_price, p.brand, p.href, p.img_src])


def save_brand_list(brands):
	with open('brands.csv', 'w', newline='', encoding='utf8') as outfile:
		writer = csv.writer(outfile)
		for b in brands:
			writer.writerow([b.strip()])


def clear_console():
	os.system('cls' if os.name == 'nt' else 'clear')


def display_brands():
	display_message = ''
	with open('brands.csv', newline='') as file:
		reader = csv.reader(file)
		brands = list(reader)
		counter = 1
		for b in brands:
			print(str(counter) + ': ' + b[0])
			counter += 1