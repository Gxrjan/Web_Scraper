class Product():
	"""This data represents a product from brandshop.
	It has a is_on_sale field which is True if this product is on sale
	current_price is a field that stores it's current price
	and regular_price that stores it's regular price for the product, that is on sale"""
	def __init__(self, product_id, product_name, is_on_sale, current_price, regular_price):
		self.product_id = product_id
		self.product_name = product_name
		self.is_on_sale = is_on_sale
		self.current_price = current_price
		self.regular_price = regular_price

	def __eq__(self, other):
		return self.product_id == other.product_id and self.product_name == other.product_name

	def __hash__(self):
		return hash(str(self.product_id))

	def __str__(self):
		return self.product_name

	def __repr__(self):
		return self.product_name


class Brand():
	"""Class representing Brand"""
	def __init__(self, brand_id):
		self.brand_id = brand_id
		self.brand_name = brand_name
