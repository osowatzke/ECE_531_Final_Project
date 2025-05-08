#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 gr-xm_module author.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class mfp_align(gr.basic_block):
    """
    Master Frame Preamble (MFP) Detector
    
    Detects MFP and aligns data so MFP occurs immediately before frame
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
            out_sig=[(np.complex64, self.FSP_SEP), (np.float32, self.FSP_SEP), np.float32])

        mfp_taps = np.flip(np.conj(np.array(self.mfp)))
        self.mfp_filt = filt(mfp_taps, dtype=np.complex64)
        self.mfp_len = len(mfp_taps)
        self.mfp_found = False
        self.fsps_left = self.NUM_FSP 
        self.frame_count = 0
        self.plot_data = []
        
    def general_work(self, input_items, output_items):
        
        samples_consumed = min(len(item) for item in output_items)
        samples_consumed = min(len(input_items[0]), samples_consumed)
        
        num_out = [0, 0]
        produced = 0  
        for item in input_items[0][:samples_consumed]:
        
            corr = np.abs(self.mfp_filt(item))
            avg_power = np.mean(corr)
            idx = np.argmax(corr)
            
            if self.mfp_found:
                self.fsps_left -= 1
                
                # Update plot for each MFP
                if self.fsps_left == 0:
                    self.fsps_left = self.NUM_FSP
                    self.plot_data = corr
                    self.frame_count += 1
                    
                # Plot routine is happiest when it gets multiple inputs
                output_items[0][produced][:] = item
                output_items[1][produced][:] = self.plot_data
                output_items[2][produced] = np.float32(self.frame_count)
                produced += 1
                
            elif corr[idx]/avg_power > 4 and idx == (len(corr) - 1):
                self.mfp_found = True
                self.fsps_left = self.NUM_FSP
                self.plot_data = corr
                     
        self.consume(0, samples_consumed)
        return produced #min(length for length in num_out) #num_out[1] # 0 #gr.basic_block.WORK_DONE

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
