#This is designed to hold the api functions
from bittrex import Bittrex
from binance.client import Client
from config import *
import time
import pandas as pd
import datetime
import requests as rq
import json


#definitions
p = Bittrex(api_key_bittrex, api_secret_bittrex)
client = Client(api_key_binance, api_secret_binance)


def send_notification(title, body):
	data_send = {"type": "note", "title": title, "body": body}
	resp = rq.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
						 headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
	if resp.status_code != 200:
		raise Exception('Something wrong')
	else:
		print('sent')

def getfiat(btc):
	r = rq.get(url='https://blockchain.info/ticker', params='')
	data = r.json()
	usd = data['USD']['sell']
	aud = data['AUD']['sell']
	audprice = float(aud)*float(btc)
	usdprice = float(usd)*float(btc)
	return audprice, usdprice

def getbinancebalance():
	info = client.get_exchange_info()
	info = info['symbols']
	coins = []
	column_headers = ['coin','quantity','last','BTC value']
	account = pd.DataFrame(columns=column_headers)
	for item in info:
		coin = item['baseAsset']
		if coin:
			coins.append(coin)
	listcoins = list(set(coins))
	for item in listcoins:
		balance = client.get_asset_balance(asset=item)
		quantity = float(balance['free'])
		if quantity > 0.0:
			if 'BTC' not in item:
				market = item.replace(item,'%sBTC'%(item))
				depth = client.get_order_book(symbol=market)
				last = depth['asks'][0][0]
				last = '{:.8f}'.format(float(last))
				quantity = '{:.8f}'.format(quantity)
				value = float(last)*float(quantity)
				value = '{:.8f}'.format(value)
				account = account.append({'coin':market,'quantity':quantity,'last':last,'BTC value':value}, ignore_index=True)
			if 'BTC' in item:
				last = '{:.8f}'.format(0)
				quantity = '{:.8f}'.format(float(quantity))
				value = '{:.8f}'.format(float(quantity))
				account = account.append({'coin':item,'quantity':quantity,'last':last,'BTC value':value}, ignore_index=True)
	total = pd.to_numeric(account['BTC value'])
	total_btc = total.sum()
	total_btc = '{:.8f}'.format(total_btc*0.975)
	return account, total_btc

def getbittrexbalance():
	balance = p.get_balances()
	balance = balance['result']
	column_headers = ['coin','quantity','last','BTC value']
	account = pd.DataFrame(columns=column_headers)
	for item in balance:
		if item['Balance'] > 0.0:
			balance = '{:.8f}'.format(item['Balance'])
			coin = item['Currency']
			if 'BTC' in coin:
				last = float(item['Balance'])
				value = float(item['Balance'])
				value = '{:.8f}'.format(value)
				last = '{:.8f}'.format(last)
				account = account.append({'coin':item['Currency'],'quantity':balance,'last':last,'BTC value':value}, ignore_index=True)
			if 'BTC' not in coin:
				coin = coin.replace(coin,'BTC-%s'%(coin))
			market = p.get_marketsummary(coin)
			#print(market)
			if market['success'] == True:
				last = market['result']
				last = last[0]['Last']
				value = float(last)*float(balance)
				value = '{:.8f}'.format(value)
				last = '{:.8f}'.format(last)
				account = account.append({'coin':item['Currency'],'quantity':balance,'last':last,'BTC value':value}, ignore_index=True)
	total = pd.to_numeric(account['BTC value'])
	total_btc = total.sum()
	total_btc = '{:.8f}'.format(total_btc*0.975)
	return account, total_btc
