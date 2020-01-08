import time
import win32ui, dde
from pywin.mfc import object


class DDETopic(object.Object):
    def __init__(self, topicName):
        self.topic = dde.CreateTopic(topicName)
        object.Object.__init__(self, self.topic)
        self.items = {}

    def setData(self, itemName, value):
        try:
            self.items[itemName].SetData( str(value) )
        except KeyError:
            if itemName not in self.items:
                self.items[itemName] = dde.CreateStringItem(itemName)
                # self.items[itemName] = dde.CreateStringItem(itemName)
                self.topic.AddItem( self.items[itemName] )
                self.items[itemName].SetData( str(value).encode() )


ddeServer = dde.CreateServer()
ddeServer.Create('Orbitron')
ddeTopic = DDETopic('Tracking')
ddeServer.AddTopic(ddeTopic)

while True:
    yourData = "ABA" #time.ctime() + ' UP0 DN145000001 UMusb DMfm AZ040 EL005 SNNO SATELLITE'
    ddeTopic.setData('Tracking', yourData)
    win32ui.PumpWaitingMessages(0, -1)
    time.sleep(0.1)