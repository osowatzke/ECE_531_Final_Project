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
    Frame Synchronization Preamble (FSP) Detector
    
    Detects FSP and aligns data so FSP occurs on 1st output sample
    """
    
    FSP_SEP = 3456
    
    def __init__(self, fsp=[1,1,1,-1,-1,1,-1]):
        gr.basic_block.__init__(self,
            name="preamble_detector",
            in_sig=[np.complex64],
            out_sig=[(np.complex64, self.FSP_SEP),(np.float32, self.FSP_SEP),(np.float32, self.FSP_SEP)])

        fsp_taps = np.flip(np.conj(np.array(fsp)))
        self.fsp_filt = filt(fsp_taps, dtype=np.complex64)
        self.fsp_len = len(fsp_taps)
        
        self.sample_buffer = np.array([],dtype=np.complex64)
        self.output_buffer = np.zeros(3*self.FSP_SEP, dtype=np.complex64)
        self.corr_buffer   = np.zeros(3*self.FSP_SEP, dtype=np.float32)
        
        self.idx = -np.ones(3,dtype=np.int32)
        self.last_idx = -1

    def general_work(self, input_items, output_items):
        
        buffer_size = min(len(output_items[0]), len(output_items[1]), len(output_items[2]))
        samples_consumed = min(buffer_size*self.FSP_SEP - len(self.sample_buffer) - 2, len(input_items[0]))
        self.sample_buffer = np.concatenate((self.sample_buffer, input_items[0][:samples_consumed]))
        produced = 0
        
        while len(self.sample_buffer) >= self.FSP_SEP:
        
            x = self.sample_buffer[:self.FSP_SEP]
            self.sample_buffer = self.sample_buffer[self.FSP_SEP:]      
            self.output_buffer = np.concatenate((self.output_buffer[self.FSP_SEP:], x))
            
            corr = np.abs(self.fsp_filt(x))
            idx = np.argmax(corr)
            avg_pwr = np.sum(np.abs(corr))/len(corr)
            
            if (corr[idx]/avg_pwr > 4):
                idx += self.FSP_SEP - self.fsp_len + 1
            else:
                idx = -1
            
            self.corr_buffer = np.concatenate((self.corr_buffer[self.FSP_SEP:], corr))
            self.idx = np.concatenate((self.idx[1:], np.array([idx])))
            
            # Keep track of last good index
            # Replace up to 1 missing detection in a row
            idx = self.idx[1]
            self.last_idx = idx
            if idx < 0:
                idx = self.last_idx
                
            self.last_idx = idx
            
            if idx > 0:
                output_items[0][produced][:] = self.output_buffer[idx:(idx + self.FSP_SEP)]              
                output_items[1][produced][:] = self.corr_buffer[self.FSP_SEP:2*self.FSP_SEP]
                output_items[2][produced][:] = self.corr_buffer[idx:(idx + self.FSP_SEP)]
                
                produced += 1
            
        self.consume(0, samples_consumed)
        return produced

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
