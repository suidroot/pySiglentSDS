#!/usr/bin/env python3

'''
    Siglent SDS11102CML Interface

    https://siglentna.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf
    https://ktln2.org/2018/02/20/control-siglent-oscilloscope/
    https://siglentna.com/application-note/programming-example-sds-oscilloscope-save-a-copy-of-a-screen-image-via-python-pyvisa/

'''

import visa
#import logger


# ['CR', 'LF', '_Resource__switch_events_off', '__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cleanup_timeout', '_encoding', '_logging_extra', '_read_termination', '_resource_manager', '_resource_name', '_session', '_values_format', '_write_termination', 'ask', 'ask_delay', 'ask_for_values', 'assert_trigger', 'before_close', 'chunk_size', 'clear', 'close', 'control_in', 'control_ren', 'disable_event', 'discard_events', 'enable_event', 'encoding', 'get_visa_attribute', 'ignore_warning', 'implementation_version', 'install_handler', 'interface_number', 'interface_type', 'io_protocol', 'is_4882_compliant', 'last_status', 'lock', 'lock_context', 'lock_excl', 'lock_state', 'manufacturer_id', 'manufacturer_name', 'maximum_interrupt_size', 'model_code', 'model_name', 'open', 'query', 'query_ascii_values', 'query_binary_values', 'query_delay', 'query_values', 'read', 'read_raw', 'read_stb', 'read_termination', 'read_termination_context', 'read_values', 'register', 'resource_class', 'resource_info', 'resource_manufacturer_name', 'resource_name', 'send_end', 'serial_number', 'session', 'set_visa_attribute', 'spec_version', 'stb', 'timeout', 'uninstall_handler', 'unlock', 'usb_control_out', 'usb_protocol', 'values_format', 'visa_attributes_classes', 'visalib', 'wait_on_event', 'write', 'write_ascii_values', 'write_binary_values', 'write_raw', 'write_termination', 'write_values']

class Sds1102cml(object):

    device = ""
    resources = ""
    DEBUG = ""

    def __init__(self, serial_number, setdebug=False):

        self.DEBUG = setdebug

        usb_ids = "0xF4EC::0xEE3A"

        resource_string = "USB0::" + usb_ids + "::" + serial_number + "::0::INSTR"

        self.resources = visa.ResourceManager('@py')
        self.device = self.resources.open_resource(resource_string)

        if self.DEBUG:
            print (self.device.query("*IDN?"))

    def __del__(self):
        self.device.close()

        if self.DEBUG:
            print("Closed")

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

    def close(self):
        self.device.close()

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

        param_vals = ['AMPL', 'BASE', 'CMEAN', 'CRMS', 'DUTY', 'FALL', 'FPRE', 'FREQ', 'MAX', 'MEAN', 'MIN', 'NDUTY', 'NWID', 'OVSN', 'OVSP', 'PER', 'PKPK', 'PWID', 'RISE', 'RMS', 'RPRE', 'TOP', 'WID']

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
        #logger.info('detected sample rate of %d' % sample_rate)

        #desc = device.write('C%d: WF? DESC' % channel)
        #logger.info(repr(device.read_raw()))

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
        print('DUMPING SCREEN')

        response = self.write('SCDP')

        with open(filename, 'w') as filehandle:
            filehandle.write(response)

        print('END')


if __name__ == '__main__':

    SERIAL_NUMBER = "SDS100P2153163"

    scope = Sds1102cml(SERIAL_NUMBER, DEBUG=True)
    print (scope.all_parameter_value('1'))
#   print ()
    scope.close()
