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
from mcush import Env



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


    #def getPlotInfoFromEvent(self, event):
    #    if not isinstance(event, wx.MouseEvent):
    #        return None
    #    x, y = event.x, event.y
    #    y = self.canvas.GetSize()[1] - y
    #    for name in self.plot.keys():
    #        box = self.plot[name].get_window_extent()
    #        if box.contains(x,y):
    #            return (name, box, x, y)
    #    return None

    def clearCursor(self, name):
        plot = self.plot[name]
        while len(plot.lines) > self.reserved_lines_num[name]:
            plot.lines.pop()
 
    #def findNearestPoint(self, datx, daty, x, y, delta):
    #    # search the nearest point to (x,y) in the range of (x-delta, x+delta)
    #    # 1. search the best X in the method of dichotomic classification
    #    #print 'find ', x, y, delta
    #    left, right = 0, len(datx)-1
    #    while left < right:
    #        mid = (left+right)/2
    #        midval = datx[mid]
    #        #print left, mid, right, midval
    #        if midval < x:
    #            #print 'midval < x', midval, x
    #            if left < mid:
    #                left = mid
    #            else:
    #                break
    #        elif midval > x:
    #            #print 'midval > x', midval, x
    #            if right > mid:
    #                right = mid
    #            else:
    #                break
    #        else:
    #            break
    #    # 2. match best point between (x-delta, x+delta)
    #    if delta:
    #        fmin = max(0,mid-delta)
    #        fmax = min(len(daty),mid+delta)
    #        ys = [(i, daty[i]) for i in range(fmin, fmax)]
    #        #print ys 
    #        ys.sort(lambda a,b: cmp(abs(a[1]-y),abs(b[1]-y)))
    #        #print ys 
    #        m = ys[0][0]
    #    else:
    #        m = mid
    #    found_x, found_y = datx[m], daty[m]
    #    #print 'found', found_x, found_y 
    #    return (found_x, found_y)

    #def updateCursor(self, name, box, x, y):
    #    self.clearCursor(name)
    #    plot = self.plot[name]
    #    datx = self.datx[name]
    #    if len(datx) == 0:
    #        return (None, None)
    #    xl, xr = plot.get_xlim()
    #    yb, yu = plot.get_ylim()
    #    x0, x1 = box.x0, box.x1
    #    y0, y1 = box.y0, box.y1
    #    newx = (xr*(x-x0)+xl*(x1-x))/(x1-x0)
    #    newy = (yu*(y-y0)+yb*(y1-y))/(y1-y0)
    #    # calculate the search range of x mapping the left N to right N pixels between the cursor
    #    PIXEL_DELTA = 10
    #    delta = int(PIXEL_DELTA * len(datx) * (xr-xl) / (datx[-1]-datx[0]) / (x1-x0))
    #    if Env.DEBUG:
    #        print xl, xr, x0, x1, '-> delta', delta
    #    newx, newy = self.findNearestPoint(self.datx[name], self.daty[name], newx, newy, delta=delta)
    #    plot.plot( [newx, newx], [yb, yu], '-', color='red' )
    #    plot.plot( [newx], [newy], 'o', color='red')
    #    for m in self.additional_cursors[name]:
    #        plot.plot( [newx*m, newx*m], [yb, yu], '-', color='#FF8080' )
    #    return (newx, newy)
 
    #def doCursorEvent(self, event):
    #    info = self.getPlotInfoFromEvent(event)
    #    if info is None:
    #        if self.click_event:  # clear all cursors when clicked on the blank area
    #            for name in self.plot.keys():
    #                self.clearCursor(name)
    #                self.hookCursorChanged( name, None, None )
    #            self.canvas.draw()
    #    else:
    #        name, box, x, y = info
    #        if not self.ignore[name]:
    #            x, y = self.updateCursor(name, box, x, y)
    #            self.hookCursorChanged( name, x, y )
    #            self.canvas.draw()

    #def getAnnotationText( self, x, y ):
    #    return 'X=%f Y=%f'% (x,y)

    #def hookCursorChanged(self, name, x, y):
    #    if self.annotation[name]:
    #        try:
    #            self.annotation[name].remove()
    #        except:
    #            pass
    #        self.annotation[name] = None
    #    if x is None or y is None:
    #        if Env.VERBOSE:
    #            print 'CursorChanged %s, cleared'% (name)
    #    else:
    #        if Env.VERBOSE:
    #            print 'CursorChanged %s, x=%.3f, y=%.3f'% (name, x, y)
    #        plot = self.plot[name]
    #        ylim_b, ylim_t = plot.get_ylim()
    #        annotation_txt = self.getAnnotationText(x, y)
    #        self.annotation[name] = plot.annotate( annotation_txt, color='red', xy=(x, y), xytext=(x, ylim_t),
    #                        horizontalalignment='center', verticalalignment='bottom', )
    #        #xlim_l, xlim_r = plot.get_xlim()
    #        #self.annotation[name] = plot.annotate( 'X: %.3f\nY: %.3f'% (x,y), color='red', xy=(x, y), xytext=(xlim_r, ylim_t-0.05*(ylim_t-ylim_b)),
    #        #                horizontalalignment='right', verticalalignment='top', )



    #def OnPress(self, event):
    #    self.click_event = True
    #    self.pressed = True
    #    self.doCursorEvent(event)
    #    event.Skip()
 
    #def OnRelease(self, event):
    #    self.pressed = False
    #    event.Skip()
 
    #def OnMotion(self, event):
    #    self.click_event = False
    #    if self.pressed:
    #        self.doCursorEvent(event)
    #    event.Skip()



 
