import minimalmodbus, time, datetime
COMPort = 'COM12' # Используемый COM-порт
MaxNum = 8 # Максимальный номер опрашиваемых силовых модулей (не считая 100-го)

def t():
	return datetime.datetime.now().strftime("%H:%M:%S")

def print_module(Addr, V):
	print(Addr, end=' ', flush=True)
	print('(', end='', flush=True)
	for j in range(3):
		print(str(V[6 + j]) + 'В/' + str(V[9 + j]) + 'мА/' + str(V[j]) + 'Вт', end='', flush=True)
		if j != 2: print('', end=' ', flush=True)
#	print(')', end=' ', flush=True)
	print(')')

def Switch(Addr,On):
	instrument = minimalmodbus.Instrument(COMPort, Addr)
	instrument.serial.baudrate = 115200
	V = 0xFFFF if On==1 else 0
	try:
		instrument.write_registers(7, [V,V,V,V])
	except:
		pass

def SwitchAll(On):
	Switch(100,On) # включаем/выключаем все каналы 100-го (защитного силового) модуля
	Switch(0,On) # включаем/выключаем все каналы всех силовых модулей (через широковещательный адрес)
	time.sleep(1.5) # ждём окончания переходных процессов в микросхемах измерения электроэнергии

def SetStandardColors():
	for i in range(MaxNum):
		instrument = minimalmodbus.Instrument(COMPort, i+1)
		instrument.serial.baudrate = 115200
		try:
			instrument.write_registers(5, [0x0201,0x0003])
		except:
			pass

def Opros():
	# опрашиваем модули
	for i in range(MaxNum+1):
		Addr = i
		if i==0: Addr=100
		instrument = minimalmodbus.Instrument(COMPort, Addr)
		instrument.serial.baudrate = 115200
		try:
			V = instrument.read_registers(13,12)
			print_module(Addr,V)
		except:
			pass
		# time.sleep(0.5)

print('  Время  Номер модуля (Напряжение(В)/Ток(мА)/Мощность(Вт) по каналам)')
while True:
	SetStandardColors()
	print('',t(),'Off:')
	SwitchAll(0) # выключаем все каналы всех модулей (несколько раз, чтобы модули не ушли в ЖМ)
	SwitchAll(0) # выключаем все каналы всех модулей
	Opros() # опрашиваем модули
#	print('')
	print('',t(),'On:')
	SwitchAll(1) # включаем все каналы всех модулей (несколько раз, чтобы модули не ушли в ЖМ)
	SwitchAll(1) # включаем все каналы всех модулей
	Opros() # опрашиваем модули
#	print('')
