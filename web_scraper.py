#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import bs4
import sys
import webbrowser
import csv
import time
from helpers import *
from classes import *

UPDATES = list()
if db_exists():
	DATA = get_data_from_db()


def scan_for_changes():
	links = get_all_brands_links()
	for link in links:
			scan_for_changes_page(link[0], link[1])


def scan_for_changes_page(href, brand):
	res = requests.get(href, verify=False)
	res.raise_for_status()
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	product_containers = soup.select('.product-container')
	for l in range(len(product_containers)):
		scan_for_changes_product(str(product_containers[l]), brand)
	if has_further_page(soup):
		href = soup.find("a", text="Далее").attrs['href']
		scan_for_changes_page(href, brand)
	else:
		return


def scan_for_changes_product(html, brand):
	update = ''
	soup = bs4.BeautifulSoup(html, "html.parser")
	product_name = soup.find("h2").text
	product_id = soup.find('div', class_='product').attrs['data-product-id']
	price_box = soup.find('div', class_="price price-box")
	href = soup.find('a').attrs['href']
	img_src = soup.find('img').attrs['src']
	if soup.find('div', class_='product outofstock'): # Надо проработать обработку продукта если он outofstock
		product_outofstock = Product(int(product_id), product_name, False, 0, 0, 'outofstock', href, img_src)
		if product_outofstock in DATA:
			DATA.remove(DATA[DATA.index(product_outofstock)])
			update += 'Продукт был удален из базы данных так как outofstock!!'
			UPDATES.append(product_outofstock.product_name + ':' + update)
		return

	if not price_box:
		product_from_page = Product(int(product_id), product_name, False, 0, 0, brand, href, img_src)
	else:
		price = price_box.text.strip()
		if price_box['data-sale'] == 'sale:true':
			prices = price.split("\n")
			current_price = str_to_int(prices[0])
			regular_price = str_to_int(prices[1])
			product_from_page = Product(
				int(product_id), product_name, True,
				int(current_price), int(regular_price), brand, href, img_src)
		else:
			price = str_to_int(price)
			product_from_page = Product(
				int(product_id), product_name, False,
				int(price), int(price), brand, href, img_src)
	print(product_from_page.product_name)
	if product_from_page not in DATA:
		DATA.append(product_from_page)
		product_news = 'Продукт был добавлен в базу данных. Цена: %s' % \
			(product_from_page.current_price)
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
			print(
				'Цена увеличилась с %s до %s' %
				(product_from_db.current_price, product_from_page.current_price))
			product_news = 'Цена увеличилась с %s до %s' % \
				(product_from_db.current_price, product_from_page.current_price)
			update = update + product_news
			product_from_db.current_price = product_from_page.current_price
			product_from_db.regular_price = product_from_page.regular_price
		elif product_from_db.current_price > product_from_page.current_price:
			print(
				'Цена уменьшилась с %s до %s' %
				(product_from_db.current_price, product_from_page.current_price))
			product_news = 'Цена уменьшилась с %s до %s' % \
				(product_from_db.current_price, product_from_page.current_price)
			update = update + product_news
			product_from_db.current_price = product_from_page.current_price
			product_from_db.regular_price = product_from_page.regular_price
		else:
			product_from_db.regular_price = product_from_page.regular_price
			print('Цена не менялась')
	if update:
		UPDATES.append(product_from_page.product_name + ':' + update)

	print('----------------------------------------------------')


def initiate_scan():
	links = get_all_brands_links()
	if db_exists():
		scan_for_changes()
		dump_data_to_db_new(DATA)
		display_updates(UPDATES)
		save_updates(UPDATES)
	else:
		print('База данных не обнаружена')
		print('Создаю базу данных...')
		create_db()
		print('база данных создана')


def main():
	while True:
		user_input = input(
			'''
			1: Начать сканирование
			2: Показать все Бренды
			3: Выйти из программы
			''')
		if user_input == '1':
			initiate_scan()
		elif user_input == '2':
			clear_console()
			display_brands()
			user_input = input('''
			Введите название бренда
			''')
			selected = list()
			for product in DATA:
				if product.brand == user_input:
					selected.append(product)
					print(str(product.product_id) + ': ' + product.product_name)
			user_input = input('''Введите номер продукта''')
			for product in selected:
				if product.product_id == int(user_input):
					webbrowser.open_new_tab(product.img_src)
		else:
			quit()


if __name__ == "__main__":
	main()
