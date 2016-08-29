import urllib.request
import urllib.parse
import html.parser


class Yahoo:

	opener = None

	def __init__(self):
		self.opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler(),urllib.request.HTTPHandler(debuglevel=0))
		self.opener.addheaders = [('User-agent', "Mozilla/5.0 (X10; Ubuntu; Linux x86_64; rv:25.0)")]


	#Scrapes option data from Yahoo Finance
	#date EX: 1416614400
	def get_option_data(self, stock_symbol, date):

		try:
			response = self.opener.open("http://finance.yahoo.com/q/op?s="+str(stock_symbol)+"&date="+str(date), timeout=30)
			data=response.read()
			data=data.decode('UTF-8')

			#decode HTML
			h=html.parser.HTMLParser()
			data=h.unescape(data)


			data=str(data.encode("UTF-8", "replace"))


			data=data.split(',"options"')
			#includes option data and the rest of the HTML page
			data=data[5]

			temp_data=data.split("_options")
			data=temp_data[0]

			#removes :{"calls":[ from beginning and " from end
			data=data[11:len(data)-2]

			temp_data=data.split('"puts":')
			calls=temp_data[0]
			puts=temp_data[1]


			to_return={}
			to_return['call']=self.not_duplicate_code(calls)
			to_return['put']=self.not_duplicate_code(puts)

			return to_return
		except Exception as error:
			print("Error: "+str(error))
			to_return={}
			to_return['call']=[]
			to_return['put']=[]
			return to_return

		

	#this exists just so I won't have to have the same code for calls and puts
	def not_duplicate_code(self, data):
		data=data.split("},{")

		for x in range(0, len(data)):
			data[x]=data[x].replace("{", "")
			data[x]=data[x].replace("}", "")
			data[x]=data[x].replace("[", "")
			data[x]=data[x].replace("]", "")
			data[x]=data[x].replace('"', "")
			data[x]=data[x].split(",")

			for y in range(0, len(data[x])):
				data[x][y]=data[x][y].split(":")

		# X  | Y | data[x][y]
		# 30 | 0 | ['contractSymbol', 'AAPL141122C00106000']
		# 30 | 1 | ['currency', 'USD']
		# 30 | 2 | ['volume', '778']
		# 30 | 3 | ['openInterest', '8591']
		# 30 | 4 | ['contractSize', 'REGULAR']
		# 30 | 5 | ['expiration', '1416614400']
		# 30 | 6 | ['lastTradeDate', '1415998724']
		# 30 | 7 | ['inTheMoney', 'true']
		# 30 | 8 | ['percentChangeRaw', '18.668596']
		# 30 | 9 | ['impliedVolatilityRaw', '0.335944140625']
		# 30 | 10 | ['impliedVolatility', '33.59']
		# 30 | 11 | ['strike', '106.00']
		# 30 | 12 | ['lastPrice', '8.20']
		# 30 | 13 | ['change', '1.29']
		# 30 | 14 | ['percentChange', '+18.67']
		# 30 | 15 | ['bid', '8.10']
		# 30 | 16 | ['ask', '8.30']

		
		new_data=[]
		for x in range(0, len(data)):

			temp_list={}
			for y in range(0, len(data[x])):
				if data[x][y][0]!="":
					item=data[x][y][0]
					# value=data[x][y][1]

					if item=="strike":
						temp_list['strike']=data[x][y][2]
					elif item=="lastPrice":
						temp_list['price']=data[x][y][2]
					elif item=="bid":
						temp_list['bid']=data[x][y][2]
					elif item=="ask":
						temp_list['ask']=data[x][y][2]
					elif item=="openInterest":
						temp_list['open_int']=data[x][y][2]
					elif item=="volume":
						temp_list['volume']=data[x][y][2]
					elif item=="impliedVolatility":
						temp_list['IV']=data[x][y][2]
						
			new_data.append(temp_list)

		return new_data


	#gets list of all available option contract expiration dates
	def get_expiration_dates(self, stock_symbol):
		# view-source:finance.yahoo.com/q/op?s=AAL
		try:
			response = self.opener.open("http://finance.yahoo.com/q/op?s="+str(stock_symbol), timeout=30)
			data=response.read()
			data=data.decode('UTF-8')
			h=html.parser.HTMLParser()
			data=h.unescape(data)
		except Exception as error:
			print("URL error (yahoo.py get_expiration_dates()): "+str(error))
			return []



		date_ids=[]
		date_strings=[]
		try:
			data=str(data.encode("UTF-8", "replace"))

			to_search='<option data-selectbox-link="/q/op?s='+str(stock_symbol)+'&date='

			date_splits=data.split(to_search)
			date_splits.pop(0)


			for x in range(0, len(date_splits)):

				# print(date_splits[x])

				temp_data=date_splits[x].split('"')

				#gets date_ids
				date_id=temp_data[0]
				date_id=date_id.strip()
				date_ids.append(date_id)

				#gets actual date
				date=temp_data[3]
				temp_date=date.split("</option>")
				#>November 22, 2014
				date=temp_date[0]
				#November 22, 2014
				date=date.replace(">", "")
				date=date.strip()
				#[0]=November
				#[1]=22,
				#[2]=2014
				date=date.split(" ")
				#[1]=22
				date[1]=date[1].replace(",", "")
				#[0]=11
				temp_strings={}
				temp_strings['january']=1
				temp_strings['february']=2
				temp_strings['march']=3
				temp_strings['april']=4
				temp_strings['may']=5
				temp_strings['june']=6
				temp_strings['july']=7
				temp_strings['august']=8
				temp_strings['september']=9
				temp_strings['october']=10
				temp_strings['november']=11
				temp_strings['december']=12
				date[0]=temp_strings[date[0].lower()]
				#['month']=11
				#['day']=22
				#['year']=2014
				temp_date={}
				temp_date['month']=int(date[0])
				temp_date['day']=int(date[1])
				temp_date['year']=int(date[2])
				date_strings.append(temp_date)
				
			
		except Exception as error:
			print("String handling error (yahoo.py get_expiration_dates()): "+str(error))
		


		to_return={}
		to_return['date_ids']=date_ids
		to_return['dates']=date_strings
		return to_return

	#converts 24.9999999995 to 25.00
	def convert_number(self, number):
		return int(number*100)/100
		