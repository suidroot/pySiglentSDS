# pySiglentSDS

This is an interface to control a Siglent SDS osciloscope over USB VISA interface. 

It provides the capablity to manually send commands and some heplper functions to gather a screen shot and write it to a file, along with collect a wave form and write it to a wav file.

https://siglentna.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf



https://ktln2.org/2018/02/20/control-siglent-oscilloscope/
https://siglentna.com/application-note/programming-example-sds-oscilloscope-save-a-copy-of-a-screen-image-via-python-pyvisa/


Example:
```
scope = Sds1102cml(serial_number=SERIAL_NUMBER, setdebug=True)
    # scope = Sds1102cml(setdebug=True)
    # device_string = scope.find_instrument(SERIAL_NUMBER)
    # scope.connect(device_string)
    print (scope.all_parameter_value('1'))
#   print ()
    scope.close()
```