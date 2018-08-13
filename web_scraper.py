#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, bs4, sys, webbrowser, csv, time
from helpers import *
from classes import *

UPDATES = list()
if db_exists():
	DATA = get_data_from_db()

def display_name_price_container_two(html):
	# отражает название и цену продуктов контейнера
	soup = bs4.BeautifulSoup(html, "html.parser")
	product_name = soup.find("h2").text
	price_box = soup.find('div', class_="price price-box")
	if not price_box:
		DATA[product_name] = (False, 0)
		return
	price = price_box.text.strip()
	print(product_name)
	if price_box['data-sale']=='sale:true':
		sale = 'True'
		prices = price.split("\n")
		price_after = str_to_int(prices[0])
		price_before = str_to_int(prices[1])
		if product_name not in DATA.keys():
			DATA[product_name] = (sale, price_before, price_after)
			print(product_name + ' добавлен(а) в список')
			NEWS.append('%s был добавлен в список. Цена %s' % (product_name, price_after))
		else:
			if DATA[product_name][0]=='False':
				print('Сейл начался!')
				if DATA[product_name][1] < price_after:
					print('Цена повысилиась с %sр до %sр' % (DATA[product_name][1], price_after))
					NEWS.append('Сейл начался! Цена на %s повысилиась с %sр до %sр' % (product_name, DATA[product_name][1], price_after))
					DATA[product_name] = (sale, price_before, price_after)
				elif DATA[product_name][1] > price_after:
					print('Цена понизилась с %sр до %sр' % (DATA[product_name][1], price_after))
					NEWS.append('Сейл начался! Цена на %s понизилась с %sр до %sр' % (product_name, DATA[product_name][1], price_after))
					DATA[product_name] = (sale, price_before, price_after)
				else:
					print('Цена осталась прежняя')
			else:
				print('Сейл все еще идет!')
				if DATA[product_name][2] < price_after:
					print('Цена повысилиась с %sр до %sр' % (DATA[product_name][2], price_after))
					NEWS.append('Цена на %s повысилиась с %sр до %sр' % (product_name, DATA[product_name][2], price_after))
					DATA[product_name] = (sale, price_before, price_after)
				elif DATA[product_name][2] > price_after:
					print('Цена понизилась с %sр до %sр' % (DATA[product_name][2], price_after))
					NEWS.append('Цена на %s понизилась с %sр до %sр' % (product_name, DATA[product_name][2], price_after))
					DATA[product_name] = (sale, price_before, price_after)
				else:
					print('Цена осталась прежняя')
	else:
		sale = 'False'
		price = str_to_int(price)
		if product_name not in DATA.keys():
			DATA[product_name] = (sale, price)
			print(product_name + ' добавлен(а) в список')
			NEWS.append('%s был добавлен в список. Цена %s' % (product_name, price))
		else:
			if DATA[product_name][0]=='False':
				print('Сейл не начался!')
				if DATA[product_name][1] < price:
					print('Цена повысилиась с %sр до %sр' % (DATA[product_name][1], price))
					NEWS.append('Цена на %s повысилиась с %sр до %sр' % (product_name, DATA[product_name][1], price))
					DATA[product_name] = (sale, price)
				elif DATA[product_name][1] > price:
					print('Цена понизилась с %sр до %sр' % (DATA[product_name][1], price))
					NEWS.append('Цена на %s понизилась с %sр до %sр' % (product_name, DATA[product_name][1], price))
					DATA[product_name] = (sale, price)
				else:
					print('Цена осталась прежняя')
			else:
				print('Сейл закончился!')
				if DATA[product_name][2] < price:
					print('Цена повысилиась с %sр до %sр' % (DATA[product_name][2], price))
					NEWS.append('Сейл закончился! Цена на %s повысилиась с %sр до %sр' % (product_name, DATA[product_name][2], price))
					DATA[product_name] = (sale, price)
				elif DATA[product_name][2] > price:
					print('Цена понизилась с %sр до %sр' % (DATA[product_name][2], price))
					NEWS.append('Сейл закончился! Цена на %s понизилась с %sр до %sр' % (product_name, DATA[product_name][2], price))
					DATA[product_name] = (sale, price)
				else:
					print('Цена осталась прежняя')
	print("----------------------------------------------")



def display_products(href):
	res = requests.get(href)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	product_containers = soup.select('.product-container')
	for l in range(len(product_containers)):
		display_name_price_container_two(str(product_containers[l]))
	if has_further_page(soup):
		print("""


			Следующая страница:


			""")
		href=soup.find("a", text="Далее").attrs['href']
		display_products(href)
	else:
		print("Конец бренда")


def scan_for_changes():
	links = get_all_brands_links()
	for link in links:
			scan_for_changes_page(link)


def scan_for_changes_page(href):
	res = requests.get(href)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	product_containers = soup.select('.product-container')
	for l in range(len(product_containers)):
		scan_for_changes_product(str(product_containers[l]))
	if has_further_page(soup):
		href=soup.find("a", text="Далее").attrs['href']
		scan_for_changes_page(href)
	else:
		return


def scan_for_changes_product(html):
	update = ''
	soup = bs4.BeautifulSoup(html, "html.parser")
	product_name = soup.find("h2").text
	product_id = soup.find('div', class_='product').attrs['data-product-id']
	price_box = soup.find('div', class_="price price-box")
	if not price_box:
		product_from_page = Product(int(product_id), product_name, False, 0, 0)
	else:
		price = price_box.text.strip()
		if price_box['data-sale']=='sale:true':
			prices = price.split("\n")
			current_price = str_to_int(prices[0])
			regular_price = str_to_int(prices[1])
			product_from_page = Product(int(product_id), product_name, True, int(current_price), int(regular_price))
		else:
			price = str_to_int(price)
			product_from_page = Product(int(product_id), product_name, False, int(price), int(price))
	print(product_from_page.product_name)
	if product_from_page not in DATA:
		DATA.append(product_from_page)
		product_news = 'Продукт %s был добавлен в базу данных. Цена: %s' % (product_from_page.product_name, 
																			product_from_page.current_price)
		print(product_news)
		update = update + product_news
	else:
		product_from_db = DATA[DATA.index(product_from_page)]
		if not product_from_page.is_on_sale and not product_from_db.is_on_sale:
			print('Сейл не начался')
		elif product_from_page.is_on_sale and product_from_db.is_on_sale:
			print('Сейл не закончился')
		elif product_from_page.is_on_sale and not product_from_db.is_on_sale:
			product_from_db.is_on_sale = product_from_page.is_on_sale
			print('Сейл начался!')
			product_news = 'Сейл начался! '
			update = update + product_news
		else:
			product_from_db.is_on_sale = product_from_page.is_on_sale
			print('Сейл закончился!')
			product_news = 'Сейл закончился! '
			update = update + product_news

		if product_from_db.current_price < product_from_page.current_price:
			print('Цена увеличилась с %s до %s' % (product_from_db.current_price, product_from_page.current_price))
			product_news = 'Цена увеличилась с %s до %s' % (product_from_db.current_price, product_from_page.current_price)
			update = update + product_news
			product_from_db.current_price = product_from_page.current_price
			product_from_db.regular_price = product_from_page.regular_price
		elif product_from_db.current_price > product_from_page.current_price:
			print('Цена уменьшилась с %s до %s' % (product_from_db.current_price, product_from_page.current_price))
			product_news = 'Цена уменьшилась с %s до %s' % (product_from_db.current_price, product_from_page.current_price)
			update = update + product_news
			product_from_db.current_price = product_from_page.current_price
			product_from_db.regular_price = product_from_page.regular_price
		else:
			product_from_db.regular_price = product_from_page.regular_price
			print('Цена не менялась')
	if update:
		UPDATES.append(product_from_db.product_name + ':' + update)	

	print('----------------------------------------------------')

		

def main():
	links = get_all_brands_links()
	if db_exists():
		scan_for_changes()
		dump_data_to_db_new(DATA)
	else:
		print('База данных не обнаружена')
		print('Создаю базу данных...')
		create_db()
		print('база данных создана')
	display_updates(UPDATES)


if __name__ == "__main__":
	main()
