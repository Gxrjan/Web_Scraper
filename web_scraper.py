#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests, bs4, sys, webbrowser, csv, time
from helpers import *

NEWS = list()


def display_name_price_container_two(html):
	# отражает название и цену продуктов контейнера
	fileRead = open('brandshop.csv', newline='', encoding='utf8')
	reader = csv.reader(fileRead)
	data = list(reader)
	data = list_to_dict(data)
	fileWrite = open('brandshop.csv', "a", newline="", encoding='utf8')
	writer = csv.writer(fileWrite)
	soup = bs4.BeautifulSoup(html, "html.parser")
	price_box = soup.find('div', class_="price price-box")
	price = price_box.text.strip()
	product_name = soup.find("a", class_="product-image")['title']
	print(product_name)
	if price_box['data-sale']=='sale:true':
		sale = True
		prices = price.split("\n")
		price_after = str_to_int(prices[0])
		price_before = str_to_int(prices[1])
		if product_name not in data.keys():
			data[product_name] = (True, price_before, price_after)
			print(product_name + ' добавлен(а) в список')
			NEWS.append('%s был добавлен в список. Цена %s' % (product_name, price_after))
		else:
			if data[product_name][0]=='False':
				print('Сейл начался!')
				if data[product_name][1] < price_after:
					print('Цена повысилиась с %sр до %sр' % (data[product_name][1], price_after))
					NEWS.append('Сейл начался! Цена на %s повысилиась с %sр до %sр' % (product_name, data[product_name][1], price_after))
					data[product_name] = (sale, price_before, price_after)
				elif data[product_name][1] > price_after:
					print('Цена понизилась с %sр до %sр' % (data[product_name][1], price_after))
					NEWS.append('Сейл начался! Цена на %s понизилась с %sр до %sр' % (product_name, data[product_name][1], price_after))
					data[product_name] = (sale, price_before, price_after)
				else:
					print('Цена осталась прежняя')
			else:
				print('Сейл все еще идет!')
				if data[product_name][2] < price_after:
					print('Цена повысилиась с %sр до %sр' % (data[product_name][2], price_after))
					NEWS.append('Цена на %s повысилиась с %sр до %sр' % (product_name, data[product_name][2], price_after))
					data[product_name] = (sale, price_before, price_after)
				elif data[product_name][2] > price_after:
					print('Цена понизилась с %sр до %sр' % (data[product_name][2], price_after))
					NEWS.append('Цена на %s понизилась с %sр до %sр' % (product_name, data[product_name][2], price_after))
					data[product_name] = (sale, price_before, price_after)
				else:
					print('Цена осталась прежняя')
	else:
		sale = False
		price = str_to_int(price)
		if product_name not in data.keys():
			data[product_name] = (sale, price)
			print(product_name + ' добавлен(а) в список')
			NEWS.append('%s был добавлен в список. Цена %s' % (product_name, price))
		else:
			if data[product_name][0]=='False':
				print('Сейл не начался!')
				if data[product_name][1] < price:
					print('Цена повысилиась с %sр до %sр' % (data[product_name][1], price))
					NEWS.append('Цена на %s повысилиась с %sр до %sр' % (product_name, data[product_name][1], price))
					data[product_name] = (sale, price)
				elif data[product_name][1] > price:
					print('Цена понизилась с %sр до %sр' % (data[product_name][1], price))
					NEWS.append('Цена на %s понизилась с %sр до %sр' % (product_name, data[product_name][1], price))
					data[product_name] = (sale, price)
				else:
					print('Цена осталась прежняя')
			else:
				print('Сейл закончился!')
				if data[product_name][2] < price:
					print('Цена повысилиась с %sр до %sр' % (data[product_name][2], price))
					NEWS.append('Сейл закончился! Цена на %s повысилиась с %sр до %sр' % (product_name, data[product_name][2], price))
					data[product_name] = (sale, price)
				elif data[product_name][2] > price:
					print('Цена понизилась с %sр до %sр' % (data[product_name][2], price))
					NEWS.append('Сейл закончился! Цена на %s понизилась с %sр до %sр' % (product_name, data[product_name][2], price))
					data[product_name] = (sale, price)
				else:
					print('Цена осталась прежняя')
	print("----------------------------------------------")
	with open('brandshop.csv', 'w', newline='', encoding='utf8') as outfile:
		w = csv.writer(outfile)
		for k,v in data.items():
			if is_on_sale(v):
				w.writerow([k, v[0], v[1], v[2]])
			else:
				w.writerow([k, v[0], v[1]])


def display_name_price_container(html):
	# отражает название и цену продуктов контейнера
	# fileRead = open('brandshop.csv', newline='', encoding='utf8')
	# reader = csv.reader(fileRead)
	# data = list(reader)
	# data = list_to_dict(data)
	fileWrite = open('brandshop.csv', "a", newline="", encoding='utf8')
	writer = csv.writer(fileWrite)
	soup = bs4.BeautifulSoup(html, "html.parser")
	price_box = soup.find('div', class_="price price-box")
	price = price_box.text.strip()
	product_name = soup.find("a", class_="product-image")['title']
	print(product_name)
	if price_box['data-sale']=='sale:true':
		prices = price.split("\n")
		price_after = str_to_int(prices[0])
		price_before = str_to_int(prices[1])
		print("Есть скидка!")
		print("Цена без скидки: " + price_before)
		print("Цена со скидкой: " + price_after)
		# if product_name not in data.keys():
		writer.writerow([product_name, True, price_before, price_after])
		# if data[product_name][2] == price_after:
		# 	print('Цена осталась прежняя')
		# else:
		# 	print('Цена изменилась!!!!!!!!!!!!!!!!!!!!!!!!')
	else:
		price = str_to_int(price)
		print("Скидок не обнаружено!")
		print("Цена: " + price)
		# if product_name not in data.keys():
		writer.writerow([product_name, False, price])
		# if data[product_name][1] == price_box.text.strip():
		# 	print('Цена осталась прежняя')
		# else:
		# 	print('Цена изменилась!!!!!!!!!!!!!!!!!!!!!!!!')
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


def main():
	links = get_all_brands_links()
	if db_exists():
		for link in links:
			display_products(link)
	else:
		print('База данных не обнаружена')
		print('Создаю базу данных.', end='')
		time.sleep(0.5)
		print('.', end='')
		for link in links:
			create_and_load_db(link)
		time.sleep(0.5)
		print('.', end='')
		time.sleep(0.5)
		print('.')
		time.sleep(0.5)
		print('база данных создана')
	display_news(NEWS)


if __name__ == "__main__":
	main()
