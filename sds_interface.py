
#
# https://siglentna.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf
# https://ktln2.org/2018/02/20/control-siglent-oscilloscope/
# https://siglentna.com/application-note/programming-example-sds-oscilloscope-save-a-copy-of-a-screen-image-via-python-pyvisa/
#

import visa
import wave

PARAM_VALS = ['AMPL', 'BASE', 'CMEAN', 'CRMS', 'DUTY', 'FALL', 'FPRE', 'FREQ', 'MAX', 'MEAN', 'MIN', 'NDUTY', 'NWID', 'OVSN', 'OVSP', 'PER', 'PKPK', 'PWID', 'RISE', 'RMS', 'RPRE', 'TOP', 'WID']
serial_number="SDS100P2153163"

resources = visa.ResourceManager('@py')
device = resources.open_resource("USB0::0xF4EC::0xEE3A::" + serial_number + "::0::INSTR")

# ['CR', 'LF', '_Resource__switch_events_off', '__class__', '__del__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cleanup_timeout', '_encoding', '_logging_extra', '_read_termination', '_resource_manager', '_resource_name', '_session', '_values_format', '_write_termination', 'ask', 'ask_delay', 'ask_for_values', 'assert_trigger', 'before_close', 'chunk_size', 'clear', 'close', 'control_in', 'control_ren', 'disable_event', 'discard_events', 'enable_event', 'encoding', 'get_visa_attribute', 'ignore_warning', 'implementation_version', 'install_handler', 'interface_number', 'interface_type', 'io_protocol', 'is_4882_compliant', 'last_status', 'lock', 'lock_context', 'lock_excl', 'lock_state', 'manufacturer_id', 'manufacturer_name', 'maximum_interrupt_size', 'model_code', 'model_name', 'open', 'query', 'query_ascii_values', 'query_binary_values', 'query_delay', 'query_values', 'read', 'read_raw', 'read_stb', 'read_termination', 'read_termination_context', 'read_values', 'register', 'resource_class', 'resource_info', 'resource_manufacturer_name', 'resource_name', 'send_end', 'serial_number', 'session', 'set_visa_attribute', 'spec_version', 'stb', 'timeout', 'uninstall_handler', 'unlock', 'usb_control_out', 'usb_protocol', 'values_format', 'visa_attributes_classes', 'visalib', 'wait_on_event', 'write', 'write_ascii_values', 'write_binary_values', 'write_raw', 'write_termination', 'write_values']

print (probe.query("*IDN?"))

def sds_run_query(device, command):

    result = device.query(command)

    return command[:-2]


def sds_all_parameter_value(device, channel):
    param_struct = {}

    result = device.query("C" + channel + ": PAVA? ALL")
    # C2:PAVA PKPK,10.08V,MAX,5.04V,MIN,-5.04V,AMPL,9.92V,TOP,4.96V,BASE,-4.96V,CMEAN,0.00mV,MEAN,0.00mV,RMS,3.52V,CRMS,3.52V,OVSN,0.81%,FPRE,47.5%,OVSP,0.81%,RPRE,0.00%,PER,99.80us,FREQ,10.02KHz,PWID,50.40us,NWID,49.60us,RISE,29.20us,FALL,29.20us,WID,1.75ms,DUTY,50.50%,NDUTY,49.70%
    result_trim = result[8:-2]

    counter = 0
    while counter <= len(result_trim):

        param_struct[result_trim[counter]] = result_trim[counter+1]
        counter +=2

    return param_struct    
    
def sds_all_parameter_value(device, channel, val):

    # C2:PAVA AMPL,9.92V
    result = device.query("C" + channel + ": PAVA? " + val.upper())

    result_return = result[8:-2].split(",",1)[1]

    return result_return

def sds_dl_waveform(device, outfilename, channel):

    sample_rate = device.query('SANU C%d?' % channel)

    sample_rate = int(sample_rate[len('SANU '):-2])
    logger.info('detected sample rate of %d' % sample_rate)

    #desc = device.write('C%d: WF? DESC' % channel)
    #logger.info(repr(device.read_raw()))

    # the response to this is binary data so we need to write() and then read_raw()
    # to avoid encode() call and relative UnicodeError
    logger.info(device.write('C%d: WF? DAT2' % (channel,))) 

    response = device.read_raw()

    if not response.startswith('C%d:WF ALL' % channel):
        raise ValueError('error: bad waveform detected -> \'%s\'' % repr(response[:80]))

    index = response.index('#9')
    index_start_data = index + 2 + 9
    data_size = int(response[index + 2:index_start_data])
    # the reponse terminates with the sequence '\n\n\x00' so
    # is a bit longer that the header + data
    data = response[index_start_data:index_start_data + data_size]
    logger.info('data size: %d' % data_size)

    fd = wave.open(outfilename, "w")
    fd.setparams((
        1,               # nchannels
        1,               # sampwidth
        sample_rate,     # framerate
        data_size,       # nframes
        "NONE",          # comptype
        "not compresse", # compname
    ))
    fd.writeframes(data)
    fd.close()

    logger.info('saved wave file')

def sds_dl_dumpscreen(device, filehandle):
    logger.info('DUMPING SCREEN')

    device.write('SCDP')
    response = device.read_raw()

    filehandle.write(response)
    filehandle.close()

    logger.info('END')


def main():


if __name__ == '__main__':
