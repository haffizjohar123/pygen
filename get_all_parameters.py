import pandas as pd
import minimalmodbus as modbus
import os.path
from  serial.tools.list_ports import comports
from time import sleep

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


config_file_path=get_config_file_path()
paralist_file_path=get_paralist_file_path()
config_file=get_config_file(config_file_path)
paralist_file=get_paralist_file(paralist_file_path)
usb_port=get_comport_dev()

print('CONFIG PATH:'+config_file_path)
print('PARALIST PATH:'+paralist_file_path)
print(config_file)
print(paralist_file)
print('USB DEV:'+usb_port)



baudrate=get_baudrate(config_file)

start_reg=get_csv_value(config_file,'config_name','value','START_REG')
device_address=get_csv_value(config_file,'config_name','value','DEVICE_ADD')
print('BAUDRATE:'+str(baudrate))
print('START_REGISTER:' + str(start_reg))

paralist_num=len(paralist_file)

for i in range (0,paralist_num):
	para_name=paralist_file['para_name'][i]
	para_address=get_csv_value(paralist_file,'para_name','register_address',para_name)
	unit=paralist_file['dimension'][i]
	para_decimal =int( paralist_file['decimal'][i])
	modbus_value=get_modbus_data(usb_port,baudrate,para_address-start_reg,para_decimal,device_address,3)
	print(para_name + ':' + str(para_address)+'-----> ' + str(modbus_value)+' ' + unit)
	sleep(0.2)
