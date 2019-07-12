# encoding:utf8
__doc__ = 'matplotlib plot utilities'
__author__ = 'Peng Shulin <trees_peng@163.com>'
import wx
from wx import Panel
import matplotlib
#matplotlib.use('wxagg', warn=False)
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg


class PlotPanel(Panel):

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, 
                style=wx.TAB_TRAVERSAL|wx.NO_BORDER, name='PlotPanel', 
                has_navigator=True, demo_plot=False,
                dpi=80, figure_size=(4,3), facecolor='white', 
                plot_parms_left=0.1, plot_parms_right=0.95, plot_parms_top=0.95, 
                plot_parms_bottom=0.1, plot_parms_hspace=0.3, plot_parms_wspace=0.3  ):

        Panel.__init__( self, parent, id, pos, size, style, name )
        self.has_navigator = has_navigator
        params = matplotlib.figure.SubplotParams(left=plot_parms_left, right=plot_parms_right, 
                                    top=plot_parms_top, bottom=plot_parms_bottom, 
                                    hspace=plot_parms_hspace, wspace=plot_parms_wspace)
        self.fig = Figure(figure_size, facecolor=facecolor, dpi=dpi, subplotpars=params)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.canvas = FigureCanvasWxAgg(self, wx.ID_ANY, self.fig)
        _w, _h = self.canvas.GetMinSize() 
        self.sizer.Add( self.canvas, 1, wx.EXPAND)
        if self.has_navigator:
            self.toolbar = NavigationToolbar2WxAgg(self.canvas)
            _w2, _h2 = self.toolbar.GetMinSize()
            self.sizer_toolbar = wx.BoxSizer(wx.HORIZONTAL)
            self.sizer_toolbar.Add( self.toolbar, 1, wx.EXPAND)
            self.sizer.Add( self.sizer_toolbar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        #self.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnPress)
        #self.canvas.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        #self.canvas.Bind(wx.EVT_MOTION, self.OnMotion)
        if self.has_navigator:
            self.SetMinSize( (max(_w,_w2), _h+_h2) )
        else:
            self.SetMinSize( (_w,_h) )
        self.plot = {}
        self.datx = {}
        self.daty = {}
        self.reserved_lines_num = {}
        self.ignore = {}
        self.annotation = {}
        self.additional_cursors = {}
        self.pressed = False
        if demo_plot:
            self.initDemoPlot()

    def clear(self):
        self.fig.clear()

    def draw(self):
        self.canvas.draw()

    def addSubPlot( self, name, position, ignore=False, additional_cursors=[0.5, 2, 3, 4] ):
        plot = self.fig.add_subplot(position)
        self.plot[name] = plot
        self.datx[name] = []
        self.daty[name] = []
        self.reserved_lines_num[name] = 1
        self.annotation[name] = None
        self.additional_cursors[name] = additional_cursors
        self.ignore[name] = ignore
        return plot

    def setDat(self, name, datx, daty):
        self.datx[name] = datx
        self.daty[name] = daty
        
    def initDemoPlot(self):
        p1 = self.addSubPlot( 'demo1', 221 )
        p2 = self.addSubPlot( 'demo2', 222 )
        p3 = self.addSubPlot( 'demo3', 212 )
        p1.grid(True, which='major', linestyle='dotted')
        p2.grid(True, which='major', linestyle='dotted')
        p3.grid(True, which='major', linestyle='dotted')
        from math import sin
        from random import random
        datx = range(0, 1000)
        daty = [ sin(x/3.0) + random()*2 for x in datx ]
        p1.plot( datx, daty )
        p1.set_ylim( auto=False )
        self.setDat('demo1', datx, daty)
        p2.plot( datx, daty )
        p2.set_ylim( auto=False )
        self.setDat('demo2', datx, daty)
        p3.plot( datx, daty )
        p3.set_ylim( auto=False )
        self.setDat('demo3', datx, daty)


    def clearCursor(self, name):
        plot = self.plot[name]
        while len(plot.lines) > self.reserved_lines_num[name]:
            plot.lines.pop()
 
