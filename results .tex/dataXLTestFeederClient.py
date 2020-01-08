from mDataStore.dataFeeder import xlBlpFeederClient
import mUtil as uu

if __name__ == '__main__':
    ipBlp=uu.getBLPIP()
    client = xlBlpFeederClient( server_addr=[(ipBlp,8021)],maxHist=10)

    # client.subscribe(['ES1 Index'], ['LAST_PRICE'])
    # client.subscribe(['BZ1 Index'], ['LAST_PRICE'])
    client.addSheet('rt')

    client.listen()


