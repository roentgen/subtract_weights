#! /usr/bin/env python
# -*- Mode: Python -*-
# -*- coding: utf-8 -*-

import sys
import math
import lwsdk

__author__     = "roentgen"
__date__       = "2017/11/30"
__copyright__  = "(C) roentgen"
__version__    = "1.0"
__maintainer__ = "roentgen"
__email__      = ""
__status__     = "test"
__lwver__      = "11"

class SubtractWeights(lwsdk.ICommandSequence):
    def __init__(self, context):
        super(SubtractWeights, self).__init__()
        self._target = ''
        self._base = ''
        
    def name_items(self, ctrl, param, row) :
        return lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_WGHT, row)
    def count_items(self, ctrl, param) :
        return lwsdk.LWObjectFuncs().numVMaps(lwsdk.LWVMAP_WGHT)
    def fast_point_scan(self, point_list, point_id):
        point_list.append(point_id)
        return lwsdk.EDERR_NONE
    # LWCommandSequence -----------------------------------
    def process(self, mod_command):
        ui = lwsdk.LWPanels()
        panel = ui.create('Subtract Weight')
        c = panel.listbox_ctl('Base Map', 300, 16, self.name_items, self.count_items)
        
        panel.align_controls_vertical([c])
        panel.size_to_layout(1, 1)
        
        if panel.open(lwsdk.PANF_BLOCKING | lwsdk.PANF_CANCEL) == 0:
            ui.destroy(panel)
            return lwsdk.AFUNC_OK
        self._base = lwsdk.LWObjectFuncs().vmapName(lwsdk.LWVMAP_WGHT, c.get_int())
        print('listed base weight: %s' % self._base)
        
        ui.destroy(panel)
        selname,selid = lwsdk.LWStateQueryFuncs().vmap(lwsdk.LWM_VMAP_WEIGHT)
        self._target = selname
        print('selected weight map id: %d' % selid)
        print('selected weight map name: %s' % selname)
        
        op = mod_command.editBegin(0, 0, lwsdk.OPSEL_USER)
        if not op:
            print >>sys.stderr, 'failed to editBegin'
            return lwsdk.AFUNC_OK
        
        result = lwsdk.EDERR_NONE
        try:
            selpoints = []
            result = op.fastPointScan(op.state, self.fast_point_scan, (selpoints,), lwsdk.OPLYR_FG, 1)
            if result != lwsdk.EDERR_NONE:
                op.done(op.state, result, 0)
                return lwsdk.AFUNC_OK
            print('selected points: %d' % len(selpoints))
            #selpoints = op.genPoints(op.state, lwsdk.OPLYR_FG, 1)
            for p in selpoints:
                # get base value
                op.vMapSelect(op.state, self._base, lwsdk.LWVMAP_WGHT, 1)
                b = op.pointVGet(op.state, p)[1]
                print ('pt:%d' % p)
                if (b != None) :
                    print ('w(B):%f' % b)
                # get target value
                op.vMapSelect(op.state, self._target, lwsdk.LWVMAP_WGHT, 1)
                v = op.pointVGet(op.state, p)[1]
                if (v != None) :
                    print ('w(A):%f' % v)
                if (b != None) :
                    v = 1.0 - b
                else :
                    v = 1.0
                op.pntVMap(op.state, p, lwsdk.LWVMAP_WGHT, self._target, [v])
        except:
            result = lwsdk.EDERR_USERABORT
            raise
        finally:
            op.done(op.state, result, 0)
        return lwsdk.AFUNC_OK


ServerTagInfo = [
    ("Subtract Weights", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH),
    ("SubtractWeights", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH),
    ("Utilities/Python", lwsdk.SRVTAG_MENU | lwsdk.LANGID_USENGLISH)
]

ServerRecord = {lwsdk.CommandSequenceFactory("LW_PySubtractWeights", SubtractWeights) : ServerTagInfo}
