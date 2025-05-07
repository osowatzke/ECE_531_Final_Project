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

class preamble_detector(gr.basic_block):
    """
    docstring for block preamble_detector
    """
    
    # FSP = [-1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,
    #     1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1] 
    
    FSP_SEP = 3456
    
    def __init__(self, fsp=[1,1,1,-1,-1,1,-1]):
        gr.basic_block.__init__(self,
            name="preamble_detector",
            in_sig=[np.complex64],
            #out_sig=[np.float32])
            out_sig=[(np.float32, self.FSP_SEP)])

        fsp_taps = np.flip(np.conj(np.array(fsp)))
        self.fsp_filt = filt(fsp_taps)
        
        self.sample_buffer = np.array([],dtype=np.complex64)

    def general_work(self, input_items, output_items):
        
        self.sample_buffer = np.concatenate((self.sample_buffer, input_items[0]))
        produced = 0
        
        while len(self.sample_buffer) >= self.FSP_SEP:
            x = self.sample_buffer[:self.FSP_SEP]
            output_items[0][:] = np.abs(self.fsp_filt(x))
            self.sample_buffer = self.sample_buffer[self.FSP_SEP:]
            produced += 1

        self.consume(0, len(input_items[0]))
        return produced


class filt:
    def __init__(self, taps):
        self.taps = np.array(taps)
        self.filter_state = np.zeros(len(taps)-1, dtype=np.complex64)
        
    def __call__(self, x):
        x = np.array(x)
        y = np.convolve(x,self.taps,'full')
        y[:len(self.filter_state)] = y[:len(self.filter_state)] + self.filter_state
        self.filter_state = y[-len(self.filter_state):]
        y = y[:-len(self.filter_state)]
        return y
