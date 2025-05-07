#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 gr-xm_module author.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import pmt

class mfp_align(gr.basic_block):
    """
    docstring for block mfp_align
    """
    
    FSP_SEP = 3456
    NUM_FSP = 205
    mfp = [1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, 1,
        -1, -1, 1, -1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1, -1,
        -1, -1, -1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, -1, -1, 1, 1, 1, -1, 1, -1, -1]
    
    def __init__(self):
        gr.basic_block.__init__(self,
            name="mfp_align",
            in_sig=[(np.complex64, self.FSP_SEP)],
            out_sig=[(np.complex64, self.FSP_SEP), (np.float32, self.FSP_SEP)])

        self.message_port_register_out(pmt.intern("frame_count"))
        mfp_taps = np.flip(np.conj(np.array(self.mfp)))
        self.mfp_filt = filt(mfp_taps, dtype=np.complex64)
        self.mfp_len = len(mfp_taps)
        self.mfp_found = False
        self.fsps_left = self.NUM_FSP 
        self.frame_count = 0
        
    def general_work(self, input_items, output_items):
        
        samples_consumed = min(len(item) for item in output_items)
        samples_consumed = min(len(input_items[0]), samples_consumed)
        
        num_out = [0, 0]
            
        for item in input_items[0][:samples_consumed]:
        
            corr = np.abs(self.mfp_filt(item))
            avg_power = np.mean(corr)
            idx = np.argmax(corr)
            
            if self.mfp_found:
                self.fsps_left -= 1
                if self.fsps_left == 0:
                    self.fsps_left = self.NUM_FSP
                    output_items[1][num_out[1]][:] = corr
                    num_out[1] += 1
                    self.frame_count += 1
                    msg = pmt.to_pmt({'frame_count': self.frame_count})
                    self.message_port_pub(pmt.intern("frame_count"), msg)
                output_items[0][num_out[0]][:] = item
                num_out[0] += 1
            elif corr[idx]/avg_power > 4 and idx == (len(corr) - 1):
                self.mfp_found = True
                self.fsps_left = self.NUM_FSP
                output_items[1][num_out[1]][:] = corr
                # print(item[idx], corr[idx])
                num_out[1] += 1        
        
        self.produce(0,num_out[0])
        self.produce(1,num_out[1])            
        self.consume(0, samples_consumed)
            
        return 0 #num_out[1] # 0 #gr.basic_block.WORK_DONE

class filt:
    def __init__(self, taps, dtype=np.complex64):
        self.taps = np.array(taps)
        self.filter_state = np.zeros(len(taps)-1, dtype=dtype)
        
    def __call__(self, x):
        x = np.array(x)
        y = np.convolve(x,self.taps,'full')
        y[:len(self.filter_state)] = y[:len(self.filter_state)] + self.filter_state
        self.filter_state = y[-len(self.filter_state):]
        y = y[:-len(self.filter_state)]
        return y
