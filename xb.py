from xbee import ZigBee
import serial
import time
import datetime
import MySQLdb as mydb
import struct
 
PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
db=mydb.connect("localhost","root","abu","sensor")
cursor=db.cursor()
def save_to_database(st,sh,sw,sl):
    #d='now()'
    d = time.strftime("%Y-%m-%d")
    t = time.strftime("%H:%M:%S")

    cursor.execute("""INSERT INTO data VALUES (%s,%s,%s,%s,%s,%s,%s)""",(0,st,sh,sw,sl,d,t))
    #cursor.execute("INSERT INTO data(temp,hum,water,light) VALUES ('st','sh','sw','sl',now(),now())")   
    db.commit()
    
def hex(bindata):
    return ''.join('%02x' % ord(byte) for byte in bindata)
 
# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)
 
# Create API object
xbee = ZigBee(ser,escaped=True)
 
# Continuously read and print packets
while True:
    try:
        response= xbee.wait_read_frame()
        sa = hex(response['source_addr_long'][4:])
        rf = hex(response['rf_data'])
        datalength=len(rf)
         #if datalength is compatible with two floats
         #then unpack the 4 byte chunks into floats
        if datalength==32:
            h=struct.unpack('f',response['rf_data'][0:4])[0]
            t=struct.unpack('f',response['rf_data'][4:8])[0]
            w=struct.unpack('f',response['rf_data'][8:12])[0]
            l=struct.unpack('f',response['rf_data'][12:16])[0]
            print sa,' ',rf,' t=',t,'h=',h,'w=',w,'l=',l
            save_to_database(t,h,w,l)
            # if it is not two floats show me what I received
        else:
            print sa,' ',rf
    except KeyboardInterrupt:
        break
         
ser.close()
#db.close()
