# -*- coding: utf-8 -*-
# Agilent_MXA_N9020A.py class, to perform the communication between the Wrapper and the device
#Thomas Weissl ,2012
#
#Based on a script written by
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <qtlab@mcschaafsma.nl>, 2008
# Guenevere Prawiroatmodjo <guen@vvtp.tudelft.nl>, 2009
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import qt
from instrument import Instrument
import visa
import types
import logging
from numpy import pi
import struct
import numpy as np
import time

class Agilent_MXA(Instrument):
    '''
    This is the python driver for the Agilent_MXA_N9020A
    Spectrum Analyzer

    Usage:
    Initialize with
    <name> = instruments.create('name', 'Agilent_MXA', address='<GPIB address>')
    '''

    def __init__(self, name, address, reset = False):#, clock=1e9, numpoints=1000):
        '''
        Initializes the MXA_N9020A

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''

        logging.debug(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])
        rm = visa.ResourceManager()

        self._address = address
        self._visainstrument = rm.open_resource(self._address)

        self.add_parameter('resBW', flags=Instrument.FLAG_GETSET, units='Hz', minval=1, maxval=3e8, type=types.FloatType)
        self.add_parameter('vidBW', flags=Instrument.FLAG_GETSET, units='Hz', minval=0.01, maxval=3e8, type=types.FloatType)
        self.add_parameter('inputattenuation', flags=Instrument.FLAG_GETSET, units='dB', minval=0, maxval=50, type=types.IntType)
        self.add_parameter('inputattenuationmode', flags=Instrument.FLAG_GETSET, option_list=['AUTO', 'MAN'], type=types.StringType)
        self.add_parameter('centerfrequency', flags=Instrument.FLAG_GETSET, units='Hz', minval=20, maxval=3e10, type=types.FloatType)
        self.add_parameter('averages', flags=Instrument.FLAG_GETSET, minval=1, maxval=10000, type=types.IntType)
        self.add_parameter('numpoints', flags=Instrument.FLAG_GETSET, minval=1, maxval=20001, type=types.IntType)
        self.add_parameter('span', flags=Instrument.FLAG_GETSET, units='Hz', minval=10, maxval=2.6e10, type=types.IntType)
        self.add_parameter('averagetype',flags=Instrument.FLAG_GETSET,  option_list=['RMS', 'LOG', 'SCALAR'], type=types.StringType)
        self.add_function('get_data')
        self.add_function('set_resBWautoOff')
        self.add_function('set_averageon')
        self.add_function('set_clearaverage')

#        self.add_parameter('interval', minval=1e-3, maxval= 500, units='s', flags=Instrument.FLAG_GETSET, type=types.FloatType)

        self.add_function('get_all')
        self.add_function('reset')


        if reset :
            self.reset()

        self.get_all()

    # Functions
    def reset(self):
        '''
        Sets the instrument to SA mode with default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Reset the instrument')
        self._visainstrument.write('CONFigure:SANalyzer:')


    def get_all(self):
        '''
        Get all parameters of the intrument

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : get all')
        self.get_resBW()
        self.get_inputattenuation()
        self.get_inputattenuationmode()
        self.get_centerfrequency()
        self.get_averages()
        self.get_numpoints()
        self.get_span()
        self.get_averagetype()

#########################################################
#
#
#                  Input Attenuation
#
#
#########################################################
    def do_get_inputattenuation(self):
        '''
        Get the input attenuation

        Input:
            None

        Output:
            inputattenuation (float) : The inputattenuation
        '''
        logging.debug(__name__ + ' : Get the input attenuation')
        return float(self._visainstrument.query(':SENSe:POWer:RF:ATTenuation? '))



    def do_set_inputattenuation(self, inputattenuation=10):
        '''
        Set the inputattenuation

        Input:
            inputattenuation (float) : input attenuation [dB]

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set input attenuation to %.6f' % (inputattenuation))
        self._visainstrument.write(':SENSe:POWer:RF:ATTenuation '+str(inputattenuation))
#########################################################
#
#
#                  Write and Read from VISA
#
#
#########################################################
    def tell(self, cmd):
        self._visainstrument.write(cmd)
    def query(self, cmd):
        res= self._visainstrument.query(cmd + '?')
        print res
        return res
#########################################################
#
#
#                  Input Attenuation Mode
#
#
#########################################################
    def do_get_inputattenuationmode(self):
        '''
        Get the input attenuation mode

        Input:
            None

        Output:
            inputattenuation (boolean) : The inputattenuation mode
        '''
        logging.debug(__name__ + ' : Get the input attenuation mode')
        ans= int(self._visainstrument.query(':SENSe:POWer:RF:ATTenuation:AUTO?'))
        if ans:
            return 'AUTO'
        else:
            return 'MAN'


    def do_set_inputattenuationmode(self, inputattenuationmode):
        '''
        Set the inputattenuation mode

        Input:
            inputattenuation (boolean) : input attenuation mode ['man' , 'auto']

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set input attenuation to '+ inputattenuationmode)
        if inputattenuationmode.upper() == 'AUTO':
            self._visainstrument.write(':SENSe:POWer:RF:ATTenuation:AUTO ON')
        else:
            self._visainstrument.write(':SENSe:POWer:RF:ATTenuation:AUTO OFF')
#########################################################
#
#
#                  number of points
#
#
#########################################################
    def do_get_numpoints(self):
        '''
        Get the number of points perform trace

        Input:
            None

        Output:
            numpoints (int) : The number of points
        '''
        logging.debug(__name__ + ' : Get the number of points')
        ans= self._visainstrument.query(':SENSe:SWEep:POINts? ')
        return ans


    def do_set_numpoints(self, numpoints=1001):
        '''
        Set the number of points perform trace

        Input:
            numpoints (int) : The number of points
        Output:
            None
        '''

        logging.debug(__name__ + ' : Set input attenuation to %.6f' % (numpoints))
        self._visainstrument.write(':SENSe:SWEep:POINts '+str(numpoints))
#########################################################
#
#
#                   Resolution Bandwidth
#
#
#########################################################
    def do_get_resBW(self):
        '''
        Get the resolution bandwidth

        Input:
            None

        Output:
            interval (float) : The interval between each cycle
        '''
        logging.debug(__name__ + ' : Get the interval between each cycle')
        return float(self._visainstrument.query(':SENSe:BANDwidth:RESolution?'))



    def do_set_resBW(self, resBW=100):
        '''
        Set the resolution bandwidth

        Input:
            resBW (float) : resolution bandwidth [Hz]

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set the interval between each cycle to %.6f' % (resBW))
        self._visainstrument.write(':SENSe:BANDwidth:RESolution '+str(resBW))
    def set_resBWautoOff(self):
        '''
        decouples resBW and Span

        Input:
            None

        Output:
        '''
        logging.debug(__name__ + ' : decouples resBW and Span ')
        datastr = self._visainstrument.write(':SENSe:BANDwidth:RESolution:AUTO 0')
#########################################################
#
#
#                   Video Bandwidth
#
#
#########################################################
    def do_get_vidBW(self):
        '''
        Get the video bandwidth

        Input:
            None

        Output:
            interval (float) : Number of points per second
        '''
        logging.debug(__name__ + ' : Get the number of points per second')
        return float(self._visainstrument.query(':SENS:BAND:VID?'))



    def do_set_vidBW(self, vidBW=100):
        '''
        Set the video bandwidth

        Input:
            vidBW (float) : video bandwidth [Hz]

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set the number of points per second %.6f' % (vidBW))
        self._visainstrument.write(':SENS:BAND:VID '+str(vidBW))
    def set_vidBWautoOff(self):
        '''
        decouples vidBW and Span

        Input:
            None

        Output:
        '''
        logging.debug(__name__ + ' : decouples vidBW and Span ')
        datastr = self._visainstrument.write(':SENS:BAND:VID:AUTO 0')
#########################################################
#
#
#                   Center Frequency
#
#
#########################################################
    def do_get_centerfrequency(self):
        '''
        Get the center frequency

        Input:
            None

        Output:
            centerfrequency (float) : The center frequency between each cycle
        '''
        logging.debug(__name__ + ' : Get the center frequency ')
        return float(self._visainstrument.query(':SENSe:FREQuency:CENTer?'))



    def do_set_centerfrequency(self, centerfrequency=1e9):
        '''
        Set the center frequency

        Input:
            centerfrequency (float) : center frequency [Hz]

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set thecentral frequency to %.6f' % (centerfrequency))
        self._visainstrument.write(':SENSe:FREQuency:CENTer '+str(centerfrequency))
#########################################################
#
#
#                   Span
#
#########################################################
    def do_get_span(self):
        '''
        Get the span

        Input:
            None

        Output:
            span(float) : The span
        '''
        logging.debug(__name__ + ' : Get the center frequency ')
        return float(self._visainstrument.query(':SENSe:FREQuency:SPAN?'))



    def do_set_span(self, span=1e9):
        '''
        Set the span

        Input:
            span (float) : center frequency [Hz]

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set the span %.6f' % (span))
        self._visainstrument.write(':SENSe:FREQuency:SPAN '+str(span))

#########################################################
#
#
#                   Averages
#
#
#########################################################
    def do_get_averages(self):
        '''
        Get the number of averages

        Input:
            None

        Output:
            averages (int) : The number of averages
        '''
        logging.debug(__name__ + ' : Get the number of averages ')
        return int(self._visainstrument.query(':SENSe:AVERage:COUNt?'))



    def do_set_averages(self, averages=100):
        '''
        Set the number of averages

        Input:
            averages (integer) : The number of averages

        Output:
            None
        '''
        logging.debug(__name__ + ' : Set the number of averages to %d' % (averages))
        self._visainstrument.write(':SENSe:AVERage:COUNt '+str(averages))

    def set_averageon(self,trace=1):
        '''
        turns on trace averaging

        Input:
            None

        Output:
        '''
        logging.debug(__name__ + ' : turns on averaging ')
        self._visainstrument.write('TRAC'+str(trace)+':TYPE AVER ')
    def set_clearaverage(self):
        '''
        clears averages

        Input:
            None

        Output:
        '''
        logging.debug(__name__ + ' : clears averages ')
        datastr = self._visainstrument.write(':SENSe:AVERage:CLEar ')
    def do_set_averagetype(self,value):
        '''
        sets averaging to RMS, LOG or SCALAR

        Input:
            type of averages: String

        Output:
            None
        '''
        logging.debug(__name__ + ' : set averaging type to ' + value)
        self._visainstrument.write(':SENSe:AVERage:TYPE '+value)
    def do_get_averagetype(self):
        '''
        gets type of averaging

        Input:
            None

        Output:
            String
        '''
        logging.debug(__name__ + ' : get averaging type')
        return self._visainstrument.query(':SENSe:AVERage:TYPE?')
#########################################################
#
#
#                   Units
#
#
#########################################################
    def get_powunits(self):
        '''
        Gets the power units

        Input:
            None

        Output:
            power units (float) : The output power units
        '''
        logging.debug(__name__ + ' : get the power units ')
        return self._visainstrument.query(':UNIT:POWer?')

    def set_powunits(self,units='DBM'):
        '''
        Sets the power units

        Input:
            DBM|DBMV|DBMA|V|W|A|DBUV|DBUA|DBUVM|DBUAM|DBPT|DBG

        Output:
            None
        '''
        logging.debug(__name__ + ' : set the power units to '+str(units))
        if str(units).upper() not in ['DBM','DBMV','DBMA','V','W','A','DBUV','DBUA','DBUVM','DBUAM','DBPT','DBG']:
            print 'Units must be one of these: DBM|DBMV|DBMA|V|W|A|DBUV|DBUA|DBUVM|DBUAM|DBPT|DBG'
        else:
            return self._visainstrument.write(':UNIT:POWer '+str(units))


#########################################################
#
#
#                   Get Data
#
#
#########################################################
    def get_data(self, n=1, enable_continuous=False):
        '''
        Reads out the nth trace

        Input:
            None

        Output:
            2D ndarray
        '''
        logging.debug(__name__ + ' : Get the data ')
        qt.mstart()
        sweep_time= float(self._visainstrument.query(':SENSe:SWEep:TIME?'))
        #print sweep_time
        self._visainstrument.write(':INIT:CONT OFF')
        self._visainstrument.write(':INIT:IMMediate')
        wait_time = 1.05*sweep_time*self.get_averages(query=False)
##        print time.ctime()
#        print 'waiting %f seconds'%wait_time
        qt.msleep(wait_time+0.5)
#        print time.ctime()
#        print 'reading'
        try:
            datastr = self._visainstrument.query(':FETCh:SANalyzer'+str(n)+'?')
        except Exception as error:
            pass
        finally:
            datastr = self._visainstrument.query(':FETCh:SANalyzer'+str(n)+'?')

        if enable_continuous:
            self._visainstrument.write(':INIT:CONT ON')
        qt.mend()
        return np.reshape(np.array(datastr.split(','),dtype=float),(-1,2))