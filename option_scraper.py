import os.path
import csv
import datetime
from datetime import date
from google import Google
from yahoo import Yahoo


class Option_Scraper:

	stock_list=[]
	google=None
	yahoo=None



	def __init__(self):
		self.google=Google()
		self.yahoo=Yahoo()

	def run(self):
		self.load_stock_list()

		if os.path.exists("./option_data")==False:
			os.mkdir("./option_data")

		#Scrapes twice because some stocks fail the first time
		for temp in range(0, 2):
			for stock in self.stock_list[x]
				self.scrape_yahoo(stock)

				#scrapes google if you want, but yahoo has more accurate data
				# self.scrape_google(stock)

			print("\n\nScraping for a 2nd time\n")




	#scrapes Google Finance for option data
	def scrape_google(self, stock_symbol):
		print("Scraping Google for "+str(stock_symbol)+"...")

		expiration_dates=self.google.get_expiration_dates(stock_symbol)


		for x in range(0, len(expiration_dates)):
			date=[]
			date.append(expiration_dates[x]['month'])
			date.append(expiration_dates[x]['day'])
			date.append(expiration_dates[x]['year'])

			#expiration date stuff
			exp_year=expiration_dates[x]['year']
			exp_month=expiration_dates[x]['month']
			exp_day=expiration_dates[x]['day']
			cur_date=self.get_current_date()
			cur_year=cur_date['year']
			cur_month=cur_date['month']
			cur_day=cur_date['day']

			#get option data if hasn't already
			path="./option_data/"+str(exp_month)+"-"+str(exp_day)+"-"+str(exp_year)+"/"+str(cur_month)+"-"+str(cur_day)+"-"+str(cur_year)+"/"+stock_symbol+"_calls.csv"
			if os.path.isfile(path)==False:
				option_data=self.google.get_option_data(stock_symbol, date)

				self.save_option_data(stock_symbol, expiration_dates[x], option_data['call'], "calls")
				self.save_option_data(stock_symbol, expiration_dates[x], option_data['put'], "puts")

	#Scrapes Yahoo finance for option data
	def scrape_yahoo(self, stock_symbol):
		print("Scraping Yahoo for "+str(stock_symbol)+"...")

		expiration_dates=self.yahoo.get_expiration_dates(stock_symbol)

		#if no option dates
		if len(expiration_dates)==0:
			return

		for x in range(0, len(expiration_dates['dates'])):
			exp_year=expiration_dates['dates'][x]['year']
			exp_month=expiration_dates['dates'][x]['month']
			exp_day=expiration_dates['dates'][x]['day']

			cur_date=self.get_current_date()
			cur_year=cur_date['year']
			cur_month=cur_date['month']
			cur_day=cur_date['day']

			#get option data if hasn't already
			path="./option_data/"+str(exp_month)+"-"+str(exp_day)+"-"+str(exp_year)+"/"+str(cur_month)+"-"+str(cur_day)+"-"+str(cur_year)+"/"+stock_symbol+"_calls.csv"
			if os.path.isfile(path)==False:
				option_data=self.yahoo.get_option_data(stock_symbol, expiration_dates['date_ids'][x])

				if option_data['call']!="":
					self.save_option_data(stock_symbol, expiration_dates['dates'][x], option_data['call'], "calls")
					self.save_option_data(stock_symbol, expiration_dates['dates'][x], option_data['put'], "puts")




	#saves option_data to CSV in ./option_data/"+expiration_date+"/"+cur_date+".csv"
	#option_type = "calls" or "puts"
	def save_option_data(self, stock_symbol, expiration_date, option_data, option_type):

		exp_year=expiration_date['year']
		exp_month=expiration_date['month']
		exp_day=expiration_date['day']

		cur_date=self.get_current_date()
		cur_year=cur_date['year']
		cur_month=cur_date['month']
		cur_day=cur_date['day']

		#creates expiration folder if it doesn't exist
		path="./option_data/"+str(exp_month)+"-"+str(exp_day)+"-"+str(exp_year)+"/"
		if os.path.isdir(path)==False:
			os.mkdir(path)

		#creates current date folder if it doesn't exist
		path+=str(cur_month)+"-"+str(cur_day)+"-"+str(cur_year)+"/"
		if os.path.isdir(path)==False:
			os.mkdir(path)

		path+=stock_symbol+"_"+str(option_type)+".csv"

		#converts option_data to csv table data stuff
		new_data=[]
		for x in range(0, len(option_data)):
			if len(option_data[x])!=0:
				try:
					temp_data=[]
					temp_data.append(option_data[x]['strike'])
					temp_data.append(option_data[x]['price'])
					temp_data.append(option_data[x]['bid'])
					temp_data.append(option_data[x]['ask'])
					temp_data.append(option_data[x]['volume'])
					temp_data.append(option_data[x]['open_int'])
					temp_data.append(option_data[x]['IV'])
				except Exception as error:
					print("Error "+str(stock_symbol)+"...")
					temp_data=[]
					temp_data.append(0)
					temp_data.append(0)
					temp_data.append(0)
					temp_data.append(0)
					temp_data.append(0)
					temp_data.append(0)
					temp_data.append(0)
				new_data.append(temp_data)


		with open( path , 'w', newline='') as file:
			contents = csv.writer(file)
			contents.writerows(new_data)

	#returns stock list retrieved from txt file
	def load_stock_list(self):
		stocks=open("./stock_list.txt")
		for symbol in stocks:
			symbol=symbol.strip()
			symbol=symbol.upper()
			self.stock_list.append(symbol)

	#returns current date in list format 2013-12-15 17:45:35.177000
	#[0]=year
	#[1]=month
	#[2]=day
	def get_current_date(self):
		curDate=str(datetime.datetime.utcnow() + datetime.timedelta(hours=-8))
		date=curDate.split(' ')
		date=date[0]
		date=date.split('-')

		to_return={}
		to_return['year']=date[0]
		to_return['month']=date[1]
		to_return['day']=date[2]
		return to_return



if __name__=="__main__":
	scraper=Option_Scraper()
	scraper.run()