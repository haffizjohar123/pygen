import pandas as pd
import minimalmodbus as modbus
import os.path
from  serial.tools.list_ports import comports
from time import sleep
import logging
import csv
import time
from datetime import date
from firebase import firebase

def check_log_file(filename):
    try:
        f=open(filename)
    except IOError:
        print('Creating log file  : history.log')
        logging.basicConfig(filename='history.log',format= '%(message)s',level=logging.INFO)
        logging.info('Date,Time,Para_name,Value,Dimension')
        f.close()



def get_comport_dev():
    devs=comports()
    usb_dev=devs[0].device
    return usb_dev


def get_config_file_path():
    homepath=os.path.expanduser('~')
    path=homepath+'/pygen/CONFIG.csv'
    return path


def get_paralist_file_path():
    homepath=os.path.expanduser('~')
    path=homepath+'/pygen/PARALIST.csv'
    return path

def get_config_file(config_path):
    config_file=pd.read_csv(config_path)
    return config_file

def get_paralist_file(paralist_path):
    paralist_file=pd.read_csv(paralist_path)
    return paralist_file




def get_baudrate(config_file):
    baudrate_index=config_file.loc[config_file['config_name']=='BAUDRATE']
    index=int(baudrate_index.index[0])
    bd=config_file['value'][index]
    baudrate=int(bd)
    return baudrate

def get_csv_value(csv_file,target_header_name,target_value_name,target_name):
    index_value=csv_file.loc[csv_file[target_header_name]==target_name]
    index_int=int(index_value.index[0])
    value=int(csv_file[target_value_name][index_int])
    return value

def get_modbus_data(usb_port,baudrate,para_reg,para_dec,device_address,function_code):
    device=modbus.Instrument(usb_port,device_address)
    device.close_port_after_each_call = True
    data=device.read_register(para_reg,para_dec,function_code,False)
    return data 

def main():
    
    from firebase import firebase
    
    config_file_path=get_config_file_path()
    paralist_file_path=get_paralist_file_path()
    config_file=get_config_file(config_file_path)
    paralist_file=get_paralist_file(paralist_file_path)
    usb_port=get_comport_dev()

    print('CONFIG PATH:'+config_file_path)
    print('PARALIST PATH:'+paralist_file_path)
    print(config_file)
    print(paralist_file)
    print('\nUSB DEV:'+usb_port)
    baudrate=get_baudrate(config_file)
    start_reg=get_csv_value(config_file,'config_name','value','START_REG')
    device_address=get_csv_value(config_file,'config_name','value','DEVICE_ADD')
    print('BAUDRATE:'+str(baudrate))
    print('START_REGISTER:' + str(start_reg))
    paralist_num=int(len(paralist_file))
    check_log_file('history.log')
    logging.basicConfig(filename='history.log',format='%(asctime)s,%(message)s', datefmt='%m/%d/%Y,%H:%M:%S',level=logging.INFO)
    logging.info('PYGEN_READ,1,BIN')
    recent_file=open('RECENT_DATA.csv','w')
    recent_writer=csv.writer(recent_file,delimiter=',',quotechar='',quoting=csv.QUOTE_NONE)
    recent_writer.writerow(['DATE','TIME','PARA_NAME','VALUE','DIMENSION'])
    today_date=date.today()
    dt=today_date.strftime('%Y-%m-%d')    
    
    firebase = firebase.FirebaseApplication('https://pygen-d1deb.firebaseio.com/',None)
    
    for i in range (0,paralist_num):
        t=time.localtime()
        read_time=time.strftime('%H:%M:%S',t)

        para_name=paralist_file['para_name'][i]
        para_address=get_csv_value(paralist_file,'para_name','register_address',para_name)
        unit=paralist_file['dimension'][i]
        para_decimal =int( paralist_file['decimal'][i])
        modbus_value=get_modbus_data(usb_port,baudrate,para_address-start_reg,para_decimal,device_address,3)
        print(para_name + ':' + str(para_address)+'-----> ' + str(modbus_value)+' ' + unit)
        logging.info(para_name+','+str(modbus_value)+',' + unit)
        recent_writer.writerow([dt,read_time,para_name,modbus_value,unit])
        firebase_para_name_data={'Value':modbus_value,
                                 'Dimension':unit,
                                 'LastUpdate':dt+' '+read_time}
        
        uploaded_para=firebase.put('/GENSET/PARAMETERS/',para_name,firebase_para_name_data)
        print('UPLOADED_PARA:')
        print(uploaded_para)
        sleep(2)
        
    logging.info('PYGEN_READ,0,BIN')
    recent_file.close()
   

if __name__=='__main__':
    main()

