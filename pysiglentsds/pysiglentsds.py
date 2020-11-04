#!/usr/bin/env python3

'''
    Siglent SDS11102CML Interface
'''

import visa


class Sds1102cml(object):

    device = ""
    resources = ""
    DEBUG = ""

    def __init__(self, serial_number='', setdebug=False):

        self.DEBUG = setdebug
        self.resources = visa.ResourceManager('@py')

        if serial_number != '':
            device_string = self.find_instrument(serial_number)
            self.connect(device_string)

    def __del__(self):
        self.device.close()

        if self.DEBUG:
            print("Closed")

    def find_instrument(self, serial_number):
        ''' Find instrument by Serial number '''
        instrument_list = self.resources.list_resources()

        return_val = 0

        for instrument in instrument_list:
            if instrument.find(serial_number) > 0:
                return_val = instrument

        if self.DEBUG:
            print("DEBUG: " + return_val)

        return return_val

    def connect(self, device_string):
        ''' Create device connection '''
        self.device = self.resources.open_resource(device_string)

        idn_val = self.get_idn()

        if self.DEBUG:
            print (idn_val)

        if idn_val == 0:
            return 0
        else:
            return 1

        return return_val


    def close(self):
        ''' close connection '''
        self.device.close()

    def get_idn(self):
        ''' Get IDN string return 0 if error'''

        idn = self.device.query("*IDN?")
        if idn == '':
            return 0
        else:
            return idn

    def write(self, command):
        ''' Run command read raw values, usefule for binary data '''

        if self.DEBUG:
            print ("DEBUG: " + command)
            print (type(command))

        self.device.write(command)
        response = self.device.read_raw()

        if response == "":
            print ("ERROR: EMPTY RESULT")

        if self.DEBUG:
            print(type(response))
            print("DEBUG: " + str(response))

        return response

    def query(self, command):
        ''' Run simple query '''

        if self.DEBUG:
            print ("DEBUG: " + command)

        response = self.device.query(command)

        if response == "":
            print ("ERROR: EMPTY RESULT")

        if self.DEBUG:
            print("DEBUG: " + response)

        return response[:-2] # trim \n\00 at end

    def all_parameter_value(self, channel):
        ''' Collect all measured values and return as dictionary '''

        param_struct = {}

        result = self.query("C" + channel + ": PAVA? ALL")
        # C2:PAVA PKPK,10.08V,MAX,5.04V,MIN,-5.04V,AMPL,9.92V,TOP,4.96V,BASE,-4.96V,CMEAN,0.00mV,MEAN,0.00mV,RMS,3.52V,CRMS,3.52V,OVSN,0.81%,FPRE,47.5%,OVSP,0.81%,RPRE,0.00%,PER,99.80us,FREQ,10.02KHz,PWID,50.40us,NWID,49.60us,RISE,29.20us,FALL,29.20us,WID,1.75ms,DUTY,50.50%,NDUTY,49.70%
        result_list = result[8:].split(",") # Trim prefix

        counter = 0
        while counter <= len(result_list)-2:
            param_struct[result_list[counter]] = result_list[counter+1]
            counter += 2

        return param_struct

    def single_parameter_value(self, channel, val):
        ''' Collect single measure value '''

        param_vals = ['AMPL', 'BASE', 'CMEAN', 'CRMS', 'DUTY', 'FALL', 'FPRE', 
            'FREQ', 'MAX', 'MEAN', 'MIN', 'NDUTY', 'NWID', 'OVSN', 'OVSP', 
            'PER', 'PKPK', 'PWID', 'RISE', 'RMS', 'RPRE', 'TOP', 'WID']

        if val not in param_vals:
            # ERROR ERROR
            return 0
        else:
            # C2:PAVA AMPL,9.92V
            result = self.query("C" + channel + ": PAVA? " + val.upper())

            result_return = result[8:].split(",",1)[1]

            return result_return

    def dl_waveform(self, outfilename, channel):
        ''' Download and store wave from as wav file '''

        import wave

        sample_rate = self.query('SANU C%d?' % channel)

        sample_rate = int(sample_rate[len('SANU '):-2])
        print ('detected sample rate of %d' % sample_rate)

        # the response to this is binary data so we need to write() and then read_raw()
        # to avoid encode() call and relative UnicodeError
        response = self.write('C%d: WF? DAT2' % (channel,))

        if not response.startswith('C%d:WF ALL' % channel):
            raise ValueError('error: bad waveform detected -> \'%s\'' % repr(response[:80]))

        index = response.index('#9')
        index_start_data = index + 2 + 9
        data_size = int(response[index + 2:index_start_data])

        # the reponse terminates with the sequence '\n\n\x00' so
        # is a bit longer that the header + data
        data = response[index_start_data:index_start_data + data_size]

        print('data size: %d' % data_size)

        wave_filehandle = wave.open(outfilename, "w")
        wave_filehandle.setparams((
            1,               # nchannels
            1,               # sampwidth
            sample_rate,     # framerate
            data_size,       # nframes
            "NONE",          # comptype
            "not compresse", # compname
        ))
        wave_filehandle.writeframes(data)
        wave_filehandle.close()

        print('saved wave file')

    def dl_dumpscreen(self, filename):
        ''' Gather Screen shot '''
        response = self.write('SCDP')

        with open(filename, 'w') as filehandle:
            filehandle.write(response)


if __name__ == '__main__':

    SERIAL_NUMBER = "SDS100P2153163"

    scope = Sds1102cml(serial_number=SERIAL_NUMBER, setdebug=True)
    # scope = Sds1102cml(setdebug=True)
    # device_string = scope.find_instrument(SERIAL_NUMBER)
    # scope.connect(device_string)
    print (scope.all_parameter_value('1'))
#   print ()
    scope.close()
