#!/usr/bin/python3.7

# Read Meters
#
# This script loops through PM800 devices on an EGX100 modbus
# gateway and extracts the name and meter readings
#

from pyModbusTCP.client import ModbusClient
import time
import string

# User Configurable Settings
#
gateway_ip = "1.1.1.1"
gateway_name = "My Site"
unit_start = 2
unit_end = 10

# Function Definitions
#

def read_meter(gw, unit):
  # Read a meter for a given modbus unit id
  # Arguments:
  # gw = IP address of the modbus gateway to use
  # unit = Modbus unit ID of the meter to read

  mbcl = ModbusClient(host=gw, port=502, auto_open=True, unit_id=unit)
  model = mbcl.read_holding_registers(0, 1) # Read model number for device

  if model[0] == 4369: # Meter is a PM8XX
    nameplate = mbcl.read_holding_registers(3001, 8) # Nameplate is 8 x 16-bit words
    wh = mbcl.read_holding_registers(1699, 4) # Energy Consumed is 4 x 16-bit words
    # Meter returns mod10 in 4 words - Convert to decimal
    wh_decoded = wh[0] + (wh[1] * 10000) + (wh[2] * 100000000) + (wh[3] * 1000000000000)

  elif model[0] == 4660: # Meter is a PM51XX
    nameplate = mbcl.read_holding_registers(29, 20) # Nameplate is 20 x 16-bit words
    wh = mbcl.read_holding_registers(3203, 4) # Energy consumed is one INT64 over 4 words
    wh_decoded = wh[3] + (wh[2] * 65535 ) + (wh [1] * 65535^2) + (wh[0] * 65535^3)

  else:
    mbcl.close()
    return # could not identify meter to read

  mbcl.close()

  # Meter was identified and read so tidy up and return the data

  kwh = wh_decoded / 1000

  meter_name = ''
  # 16 bit words need to be split into bytes and converted to ASCII
  for word16 in nameplate:
      meter_name += chr(word16 >> 8)
      meter_name += chr(word16 % 256)

  clean_metername = "".join(filter(lambda x: x in string.printable, meter_name))

  return meter_name, kwh

def main():
  print("======================================================")
  print(gateway_name + " Meter Readings " + time.strftime("%c") )
  print("======================================================")

  for meter in range(unit_start, unit_end):
    (meter_name, meter_reading) = read_meter(gateway_ip, meter)
    print("Meter Name:            " + meter_name)
    print("Current Reading (kWh): " + "{:,.3f}".format(meter_reading))
    print("======================================================")

if __name__ == "__main__":
  main()
