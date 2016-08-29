import urllib.request
import urllib.parse
from urllib import request
import html.parser
import time



class Google:
	opener = None

	def __init__(self):
		#initializes url variables
		self.opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler(),urllib.request.HTTPHandler(debuglevel=0))
		self.opener.addheaders = [('User-agent', "Mozilla/5.0 (X10; Ubuntu; Linux x86_64; rv:25.0)"])]


	#gets stock ID for retrieving option data
	def get_option_chain_underlying_id(self, stock_symbol):
		response = self.opener.open("https://www.google.com/finance/option_chain?q="+str(stock_symbol), timeout=30)
		data=response.read()
		data=data.decode('UTF-8')

		#decode HTML
		h=html.parser.HTMLParser()
		data=h.unescape(data)


		if "underlying_id" not in data:
			return ""

		temp_data=data.split('underlying_id:"')
		temp_data=temp_data[1]
		temp_data=temp_data.split('"')
		temp_data=temp_data[0]
		underlying_id=int(temp_data.strip())
		return underlying_id

	#downloads option data (strike, bid, ask, etc.)
	def get_option_data(self, stock_symbol, date):

		month=str(date[0])
		day=str(date[1])
		year=str(date[2])

		underlying_id=self.get_option_chain_underlying_id(stock_symbol)
		if underlying_id=="":
			return []

		#gets option prices from August 16, 2014
		try:
			response = self.opener.open("https://www.google.com:443/finance/option_chain?cid="+str(underlying_id)+"&expd="+str(day)+"&expm="+str(month)+"&expy="+str(year)+"&output=json", timeout=30)
			data=response.read()
			data=data.decode('UTF-8')
		except Exception as error:
			print("Google threw error: "+str(error)+". Retrying in 10 seconds")
			time.sleep(10)
			#retries
			response = self.opener.open("https://www.google.com:443/finance/option_chain?cid="+str(underlying_id)+"&expd="+str(day)+"&expm="+str(month)+"&expy="+str(year)+"&output=json", timeout=30)
			data=response.read()
			data=data.decode('UTF-8')


		#gets current price
		temp_data=data.split('underlying_price:')
		temp_data=temp_data[1]
		temp_data=temp_data.split('}')
		temp_data=temp_data[0]
		underlying_price=float(temp_data.strip())

		#if price is less than 10, or calls aren't returned
		if underlying_price<10 or "calls" not in data or "puts" not in data:
			return []

		###gets calls###

		to_return={}
		option_type="call"
		for okay in range(1, 3):
			if okay%2==0:
				option_type="put"

			#gets correct data for scraping
			temp_data=data.split(option_type)
			temp_data=temp_data[1]
			if option_type=="put":
				temp_data=temp_data.split(",calls")
				temp_data=temp_data[0]
			new_data=temp_data.split("cid")

			for x in range(0, len(new_data)):
				new_data[x]=new_data[x].split(",")

				for y in range(0, len(new_data[x])):
					new_data[x][y]=new_data[x][y].replace("'", "")
					new_data[x][y]=new_data[x][y].replace('"', "")
					new_data[x][y]=new_data[x][y].replace("{", "")
					new_data[x][y]=new_data[x][y].replace("}", "")


					new_data[x][y]=new_data[x][y].split(":")

			new_data.pop(0)

			for x in range(0, len(new_data)):

				#removes any data that isn't important
				y=0
				while y<len(new_data[x]):
					if len(new_data[x][y])>1:
						data_type=new_data[x][y][0]
						#p = price, b = bid, a = ask, oi = open interest, vol = volume, strike = strike
						if data_type!="p" and data_type!="b" and data_type!="a" and data_type!="oi" and data_type!="vol" and data_type!="strike": 
							new_data[x].pop(y)
						else:
							y+=1
					else:
						new_data[x].pop(y)

			##Example output
			# [['p', '14.60'], ['b', '11.60'], ['a', '14.45'], ['oi', '7'], ['vol', '-'], ['strike', '24.00']]
			# [['p', '12.10'], ['b', '11.60'], ['a', '12.80'], ['oi', '57'], ['vol', '14'], ['strike', '25.00']]
			# [['p', '-'], ['b', '9.60'], ['a', '11.85'], ['oi', '0'], ['vol', '-'], ['strike', '26.00']]
			# [['p', '12.25'], ['b', '9.00'], ['a', '10.80'], ['oi', '3'], ['vol', '-'], ['strike', '27.00']]
			# [['p', '9.45'], ['b', '8.60'], ['a', '9.80'], ['oi', '45'], ['vol', '-'], ['strike', '28.00']]
			# [['p', '10.25'], ['b', '7.65'], ['a', '8.85'], ['oi', '6'], ['vol', '-'], ['strike', '29.00']]
			# [['p', '7.75'], ['b', '6.70'], ['a', '7.75'], ['oi', '175'], ['vol', '17'], ['strike', '30.00']]
			# [['p', '6.55'], ['b', '5.80'], ['a', '6.75'], ['oi', '57'], ['vol', '-'], ['strike', '31.00']]
			# [['p', '6.10'], ['b', '4.90'], ['a', '5.75'], ['oi', '39'], ['vol', '-'], ['strike', '32.00']]
			# [['p', '4.75'], ['b', '3.95'], ['a', '4.75'], ['oi', '6008'], ['vol', '-'], ['strike', '33.00']]
			# [['p', '4.30'], ['b', '3.10'], ['a', '3.80'], ['oi', '20'], ['vol', '-'], ['strike', '34.00']]
			# [['p', '2.97'], ['b', '2.40'], ['a', '2.96'], ['oi', '238'], ['vol', '9'], ['strike', '35.00']]
			# [['p', '2.42'], ['b', '1.82'], ['a', '2.03'], ['oi', '299'], ['vol', '-'], ['strike', '36.00']]
			# [['p', '1.55'], ['b', '1.30'], ['a', '1.46'], ['oi', '3101'], ['vol', '828'], ['strike', '37.00']]
			# [['p', '0.92'], ['b', '0.89'], ['a', '0.96'], ['oi', '1781'], ['vol', '5849'], ['strike', '38.00']]
			# [['p', '0.65'], ['b', '0.57'], ['a', '0.68'], ['oi', '9940'], ['vol', '264'], ['strike', '39.00']]
			# [['p', '0.45'], ['b', '0.39'], ['a', '0.45'], ['oi', '6665'], ['vol', '1230'], ['strike', '40.00']]
			# [['p', '0.28'], ['b', '0.24'], ['a', '0.33'], ['oi', '2022'], ['vol', '31'], ['strike', '41.00']]
			# [['p', '0.22'], ['b', '0.14'], ['a', '0.22'], ['oi', '1100'], ['vol', '6'], ['strike', '42.00']]
			# [['p', '0.18'], ['b', '0.07'], ['a', '0.15'], ['oi', '271'], ['vol', '17'], ['strike', '43.00']]
			# [['p', '0.17'], ['b', '0.07'], ['a', '0.13'], ['oi', '255'], ['vol', '-'], ['strike', '44.00']]
			# [['p', '0.13'], ['b', '0.05'], ['a', '0.12'], ['oi', '452'], ['vol', '-'], ['strike', '45.00']]
			# [['p', '0.05'], ['b', '0.01'], ['a', '0.10'], ['oi', '201'], ['vol', '53'], ['strike', '46.00']]
			# [['p', '0.10'], ['b', '0.02'], ['a', '0.10'], ['oi', '130'], ['vol', '-'], ['strike', '47.00']]
			# [['p', '-'], ['b', '0.01'], ['a', '0.10'], ['oi', '0'], ['vol', '-'], ['strike', '48.00']]
			# [['p', '-'], ['b', '0.01'], ['a', '0.12'], ['oi', '0'], ['vol', '-'], ['strike', '49.00']]
			# [['p', '0.05'], ['b', '0.01'], ['a', '0.09'], ['oi', '14'], ['vol', '-'], ['strike', '50.00']]

			#converts option data 
			new_list=[]
			for x in range(0, len(new_data)):
				temp_list={}

				for y in range(0, len(new_data[x])):
					title=new_data[x][y][0]
					if title=="strike":
						temp_list['strike']=new_data[x][y][1]
					elif title=="p":
						temp_list['price']=new_data[x][y][1]
					elif title=="b":
						temp_list['bid']=new_data[x][y][1]
					elif title=="a":
						temp_list['ask']=new_data[x][y][1]
					elif title=="oi":
						temp_list['open_int']=new_data[x][y][1]
					elif title=="vol":
						temp_list['volume']=new_data[x][y][1]
				new_list.append(temp_list)

			new_data=new_list


			#removes any illiquid strike prices
			new_list=[]
			for x in range(0, len(new_data)):
				if new_data[x]['open_int']!="0":
					new_list.append(new_data[x].copy())

			to_return[option_type]=new_list

		return to_return



	#Gets list of all available contract expiration dates
	def get_expiration_dates(self, stock_symbol):

		underlying_id=self.get_option_chain_underlying_id(stock_symbol)
		if underlying_id=="":
			return []

		#gets option prices
		try:
			response = self.opener.open("https://www.google.com:443/finance/option_chain?cid="+str(underlying_id)+"&output=json", timeout=30)
			data=response.read()
			data=data.decode('UTF-8')
		except Exception as error:
			print("Google threw error: "+str(error)+". Retrying in 10 seconds")
			time.sleep(10)

		if "expirations:[" in data:
			#gets expiration 
			temp=data.split("expirations:[")
			temp=temp[1].split("],puts:")
			temp=temp[0]
			#temp: 
			# {y:2014,m:11,d:14},{y:2014,m:11,d:22},{y:2014,m:11,d:28},{y:2014,m:12,d:5},{y:2014,m:12,d:12},{y:2014,m:12,d:20},{y:2014,m:12,d:26},{y:2015,m:1,d:17},{y:2015,
			# m:2,d:20},{y:2015,m:3,d:20},{y:2015,m:5,d:15},{y:2016,m:1,d:15},{y:2017,m:1,d:20}

			temp=temp.split("},{")

			for x in range(0, len(temp)):
				temp[x]=temp[x].replace("{", "")
				temp[x]=temp[x].replace("}", "")

				temptemp=temp[x].split(",")
				year=int(temptemp[0].replace("y:", ""))
				month=int(temptemp[1].replace("m:", ""))
				day=int(temptemp[2].replace("d:", ""))

				new_list={}
				new_list['year']=year
				new_list['month']=month
				new_list['day']=day
				temp[x]=new_list

			return temp
			
		else:
			print("Error extrapolating expiration data (google.py: get_expiration_dates())")
			return []


	#converts 24.99999999999995 to 25.00
	def convert_number(self, number):
		return int(number*100)/100