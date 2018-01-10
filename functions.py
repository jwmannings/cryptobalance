#This is designed to hold the api functions
from bittrex import Bittrex
from config import api_key, api_secret, access_token
import time
import pandas as pd
import datetime
import requests as rq
import json


#definitions
p = Bittrex(api_key, api_secret)


def send_notification(title, body):
	data_send = {"type": "note", "title": title, "body": body}
	resp = rq.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
						 headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'})
	if resp.status_code != 200:
		raise Exception('Something wrong')
	else:
		print('sent')

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
	total_btc = total[0].sum()
	total_btc = '{:.8f}'.format(total_btc*0.975)
	return account, total_btc
