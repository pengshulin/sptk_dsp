#!/usr/bin/env python
# coding: utf8
# ShulinPeng's ToolKit for Digital Signal Processing
# Peng Shulin <trees_peng@163.com> 2017
from __future__ import unicode_literals
import os
import re
import sys
import math
import time
import signal
import random
import keyword
import numpy
import scipy
import scipy.signal
import scipy.fftpack
from Queue import Empty
from threading import Thread
from multiprocessing import Process, Queue
from math import *
from random import *
from sptk_dsp_dlg import *
import wx
import wx.lib.newevent

(RunEvent, EVT_RUN) = wx.lib.newevent.NewEvent()
LINE_LIMIT = 80

SCRIPTS_LIST = [
['FFT', r'''# Fast Fourier Transform
length = 4096
bandwidth = 5000
sample_rate = 2.56*float(bandwidth)
tick_time = 1 / sample_rate
total_time = length / sample_rate

def cutDatThreshold(dat, threshold=0.0, larger=True):
    if larger:
        for i in range(len(dat)):
            if dat[i] < threshold:
                dat[i] = threshold
    else:
        for i in range(len(dat)):
            if dat[i] < threshold:
                dat[i] = threshold

def printDat( dat, mode='f', factor=1.0 ):
    if mode == 'f':
        print 'const float dat[%d] = {'% len(dat)
    elif mode == 'i12':
        print 'const uint16_t dat[%d] = {'% len(dat)
    else:
        return
    length = len(dat)
    linelen = 0
    for i in range(length):
        d = dat[i] * factor
        if mode == 'f':
            output = '%f'% d
        elif mode == 'i12':
            output = '0x%04X'% int(d)
        if i < length-1:
            output += ','
        linelen += len(output)
        if linelen > LINE_LIMIT:
            print ''
            print output,
            linelen = len(output)
        else:
            print output,
            
    print '};'

def makeRandom( length, amp ):
    return numpy.array([ 2*amp*(random()-0.5) for i in range(length) ])

def makeImpulse( length, amp, width ):
    return numpy.array([ amp if i < width else 0 for i in range(length) ])

def makeSine( length, amp, freq, sample_rate ):
    return numpy.array([ amp*sin(i*2*pi*freq/sample_rate) for i in range(length) ])

def makeSine2( length, amp, freq, sample_rate, multi_select=1 ):
    r = []
    p, dp = 0, 2*pi*freq/sample_rate
    cnt = 0
    for i in range(length):
        if cnt % multi_select == 0:
            v = sin(p)
            r.append( v )
        else:
            r.append( 0 )
        p += dp
        if p > 2*pi:
            p -= 2*pi
            cnt += 1
    return numpy.array(r)

def makeSquare( length, amp, freq, sample_rate ):
    r, toggle = [], False
    p, dp = 0, 2*pi*freq/sample_rate
    for i in range(length):
        p += dp
        if p > pi:
            p -= pi
            toggle = not toggle
        r.append( -amp if toggle else amp )
    return numpy.array(r)

def makeTriangle( length, amp, freq, sample_rate ):
    r, toggle, v = [], False, -amp
    p, dp = 0, 2*pi*freq/sample_rate
    dv = 2*amp / (float(sample_rate)/freq/2)
    for i in range(length):
        p += dp
        if p >= pi:
            p -= pi
            toggle = not toggle
            if toggle:
                v = amp
            else:
                v = -amp
        else:
            if toggle:
                v -= dv
            else:
                v += dv
        r.append( v )
    return numpy.array(r)

def makeSawtooth( length, amp, freq, sample_rate ):
    r, v = [], amp
    p, dp = 0, 2*pi*freq/sample_rate
    dv = amp / (float(sample_rate)/freq/2)
    for i in range(length):
        p += dp
        if p > 2*pi:
            p -= 2*pi
            v = amp
        else:
            v -= dv
        r.append( v )
    return numpy.array(r)


def makeEnvelope( length, amp, freq, freq_env, sample_rate ):
    r = [ amp*sin(i*2*pi*freq/sample_rate)* \
          (2+sin(i*2*pi*freq_env/sample_rate))/3 \
            for i in range(length) ]
    return numpy.array(r)


def makeImpulse( length, amp, freq, sample_rate, init_dphase=0.0 ):
    r = []
    p, dp = 0, 2*pi*freq/sample_rate
    p += dp * init_dphase
    for i in range(length):
        v = amp * exp(-p)
        r.append( v )
        p += dp
        if p > 2*pi:
            p -= 2*pi
    return numpy.array(r)



def readFromFile( fname, cut=None, decimate=None ):
    lst = []
    f = open(fname, 'r')
    while True:
        l = f.readline()
        if not l:
            break
        if decimate:
            for i in range(decimate):
                f.readline()
        lst.append( float(l.strip()) )
        if cut and len(lst) >= cut:
            break
    return numpy.array(lst)

def resetOffset(dat):
    means = sum(dat) / len(dat) 
    return dat - means


#dat = makeRandom( length, 1 )
#dat = makeImpulse( length, 1, 10 )
#dat = makeSine( length, 1, 100, sample_rate )
#dat = makeSquare( length, 1, 100, sample_rate )
#dat = makeTriangle( length, 1, 100, sample_rate )
#dat = makeSawtooth( length, 1, 100, sample_rate )
#dat = makeEnvelope( length, 1, 100, 10, sample_rate )
dat = makeImpulse( length, 1, 100, sample_rate )
#cutDatThreshold( dat )
#dat = readFromFile( '/dev/shm/float_array', decimate=1 )
#dat = resetOffset(dat)

length = len(dat)  # reset
total_time = length / sample_rate  # reset

#printDat( (dat+1.0)/2.0, mode='i12', factor=4095 )
printDat( dat, mode='i12', factor=4095 )

FFT_DATA_MODE=False

# add window
NEED_WINDOW = False
if NEED_WINDOW:
    # TYPE:
    # boxcar, triang, blackman, hamming, hann, bartlett,
    # flattop, parzen, bohman, blackmanharris, nuttall, 
    # barthann, kaiser (needs beta), gaussian (needs std), 
    # general_gaussian (needs power, width), 
    # slepian (needs width), chebwin (needs attenuation)
    window = scipy.signal.get_window( 'hamming', len(dat) )
    dat_window = dat * window

dat_x = numpy.linspace(0, total_time, length)
if NEED_WINDOW:
    fft_raw = numpy.fft.fft( dat_window ) / (length/2)
else:
    fft_raw = numpy.fft.fft( dat ) / (length/2)
fft_abs = abs(fft_raw)
if FFT_DATA_MODE:
    fft_abs = dat 
fft_x = numpy.linspace(0, sample_rate, length, endpoint=False)
fft_phase = numpy.angle(fft_raw) / pi * 180

NEED_HILBERT = False
if NEED_HILBERT:
    dat_hilbert = scipy.fftpack.hilbert(dat)
    dat_hilbert_env = numpy.sqrt(dat**2 + dat_hilbert**2)
    fft_hilbert_raw = numpy.fft.fft( dat_hilbert ) / (length/2)
    fft_hilbert_abs = abs(fft_hilbert_raw)
    fft_hilbert_phase = numpy.angle(fft_hilbert_raw) / pi * 180

p = GETPANEL()
# plot1: source
p1 = p.addSubPlot('dat', 311, additional_cursors=[])
p1.clear()
p1.set_ylabel( 'dat' )
p1.plot( dat_x, dat, color='b' )
if NEED_WINDOW:
    p1.plot( dat_x, dat_window, color='darkblue' )
    p.reserved_lines_num['dat'] += 1
if NEED_HILBERT:
    p1.plot( dat_x, dat_hilbert, color='y' )
    p.reserved_lines_num['dat'] += 1
    p1.plot( dat_x, dat_hilbert_env, color='g' )
    p.reserved_lines_num['dat'] += 1
p.setDat( 'dat', dat_x, dat )
p1.set_xlim( left=0, right=total_time, auto=False )
p1.set_ylim( bottom=min(dat), top=max(dat), auto=False )
p1.grid(True, which='major', linestyle=':')

NEED_LOG_PLOT = False
# plot2: fft_amp
p2 = p.addSubPlot('fft_amp', 312)
p2.clear()
p2.set_ylabel( 'fft_amp' )
if NEED_LOG_PLOT:
    p2.semilogy( fft_x, fft_abs, color='b' )
else:
    p2.plot( fft_x, fft_abs, color='b' )
p.setDat( 'fft_amp', fft_x, fft_abs )
p2.grid(True, which='major', linestyle=':')
p2.set_xlim( left=0, right=fft_x[-1], auto=False )
p2.set_ylim( bottom=0, top=max(fft_abs), auto=False )

# plot3: fft_phase
p3 = p.addSubPlot('fft_phase', 313)
p3.clear()
p3.set_ylabel( 'fft_phase' )
p3.plot( fft_x, fft_phase, color='b' )
p.setDat( 'fft_phase', fft_x, fft_phase )
if NEED_HILBERT:
    p3.plot( fft_x, fft_hilbert_phase, color='y' )
    p.reserved_lines_num['fft_phase'] += 1
p3.set_xlim( left=0, right=fft_x[-1], auto=False )
p3.set_ylim( bottom=-180, top=180, auto=False )
p3.grid(True, which='major', linestyle=':')
p.draw()
'''],

['FIR', '''\
pass
'''],

]

###############################################################################
#signal_idx = 0
#def signal_handler(signum, frame):
#    global signal_idx
#    print '[%d] SIGUSR1'% signal_idx
#    signal_idx += 1
#    dialog_1.control_queue.put_nowait( "run" )
#signal.signal(signal.SIGUSR1, signal_handler)
#PIDFILE = '/dev/shm/sptk_dsp.pid'
#open( PIDFILE, 'w+' ).write( str(os.getpid()) )
#print 'PID=%d'% os.getpid()


FIFO = '/dev/shm/sptk_dsp.fifo'
if os.path.isfile( FIFO ):
    os.remove( FIFO )
if not os.path.exists( FIFO ):
    os.mkfifo( FIFO )
    os.chmod( FIFO, 0666 )

SCRIPTS_DICT = {}
for k,v in SCRIPTS_LIST:
    SCRIPTS_DICT[k] = v

class AssertError(Exception):
    pass

class StopError(Exception):
    pass

def ASSERT(condition):
    if not condition:
        raise AssertError()

def STOP(message=''):
    raise StopError(message)

def GETPANEL():
    return dialog_1.plotpanel


class MainFrame(MyFrame):
    def __init__(self, *args, **kwds):
        MyFrame.__init__( self, *args, **kwds )
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.combo_box_script.SetValue('select script')
        self.combo_box_script.AppendItems([c[0] for c in SCRIPTS_LIST]) 
        self.init_text_ctrl_script()
        self.button_run.Enable(False)
        self.SetAcceleratorTable(wx.AcceleratorTable([  \
            (wx.ACCEL_NORMAL, wx.WXK_F5,  self.button_run.GetId()),  # run
            ]))
        self.control_queue = Queue()
        self.Bind(EVT_RUN, self.OnRun)
        self.listener = Thread( target=self.listener )
        self.listener.setDaemon( 1 )
        self.listener.start()
 
    #def listener( self ):
    #    while True:
    #        try:
    #            self.control_queue.get( block=True )
    #        except Empty:
    #            break
    #        # update 
    #        wx.PostEvent( self, RunEvent() )
    
    def listener( self ):
        while True:
            try:
                cmd = open(FIFO,'r').readline().strip()
            except:
                pass
            # update 
            wx.PostEvent( self, RunEvent() )

    def OnSelectScript(self, event):
        self.info('')
        tp = self.combo_box_script.GetValue()
        if SCRIPTS_DICT.has_key(tp):
            self.text_ctrl_script.SetValue( SCRIPTS_DICT[tp] )
            self.button_run.Enable(True)
        else:
            self.button_run.Enable(False)
        event.Skip()

    def OnRun(self, event):
        print 'OnRun'
        self.run()
        event.Skip()
        
    def run(self):
        self.info('')
        script = self.text_ctrl_script.GetValue()
        try:
            code = compile(script, '', 'exec')
        except Exception as e:
            self.info(unicode(e), wx.ICON_ERROR)
            return
        t0 = time.time()
        try:
            exec( code )
        except AssertError:
            pass
        except StopError as e:
            self.info(unicode(e), wx.ICON_ERROR)
        except Exception as e:
            self.info(unicode(e))
            return
        t1 = time.time()
        print( 'time elapsed: %.1f seconds'% (t1-t0) )

    def OnClose(self, event):
        self.Destroy()
        event.Skip()
 
    def info( self, info, info_type=wx.ICON_WARNING ):
        if info:
            self.bar_info.ShowMessage(info, info_type)
        else:
            self.bar_info.Dismiss()
 
    def init_text_ctrl_script(self):
        ctrl = self.text_ctrl_script
        faces = { 'times': 'Courier New',
                  'mono' : 'Courier New',
                  'helv' : 'Courier New',
                  'other': 'Courier New',
                  'size' : 12,
                  'size2': 10,
                }
        ctrl.SetLexer(wx.stc.STC_LEX_PYTHON)
        ctrl.SetKeyWords(0, " ".join(keyword.kwlist))
        ctrl.SetProperty("tab.timmy.whinge.level", "1")
        ctrl.SetMargins(0,0)
        ctrl.SetViewWhiteSpace(False)
        ctrl.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleClearAll()
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        ctrl.StyleSetSpec(wx.stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        ctrl.StyleSetSpec(wx.stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
        ctrl.SetCaretForeground("BLACK")
        ctrl.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        ctrl.SetMarginWidth(1, 40)
    

    def OnUpdateUI(self, evt):
        ctrl = self.text_ctrl_script
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = ctrl.GetCurrentPos()

        if caretPos > 0:
            charBefore = ctrl.GetCharAt(caretPos - 1)
            styleBefore = ctrl.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and (32 < charBefore < 128):
            if chr(charBefore) in "[]{}()" and styleBefore == wx.stc.STC_P_OPERATOR:
                braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = ctrl.GetCharAt(caretPos)
            styleAfter = ctrl.GetStyleAt(caretPos)
            if charAfter and (32 < charAfter < 128):
                if chr(charAfter) in "[]{}()" and styleAfter == wx.stc.STC_P_OPERATOR:
                    braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = ctrl.BraceMatch(braceAtCaret)
        if braceAtCaret != -1  and braceOpposite == -1:
            ctrl.BraceBadLight(braceAtCaret)
        else:
            ctrl.BraceHighlight(braceAtCaret, braceOpposite)




if __name__ == "__main__":
    gettext.install("app")
    app = wx.App(0)
    app.SetAppName( 'SptkDskApp' )
    dialog_1 = MainFrame(None, wx.ID_ANY, "")
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()
