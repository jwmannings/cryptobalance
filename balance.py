from functions import *

bit = getbittrexbalance()[1]
bin = getbinancebalance()[1]
totalbtc = float(bit)+float(bin)
fiat = getfiat(totalbtc)
print("$AUD: ",fiat[0])
print("$USD: ",fiat[1])
