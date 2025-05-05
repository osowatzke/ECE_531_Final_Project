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

class preamble_detector(gr.sync_block):
    """
    docstring for block preamble_detector
    """
    
    FSP = [-1,  1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,
        1, -1,  1, -1, -1,  1,  1, -1,  1,  1,  1, -1, -1, -1, -1,  1] 
    
    def __init__(self, fsp=[1,1,1,-1,-1,1,-1]):
        gr.sync_block.__init__(self,
            name="preamble_detector",
            in_sig=[np.complex64],
            #out_sig=[np.float32])
            out_sig=[(np.float32, 3456)])
            
        self.mf = np.array([1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, -1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, -1, 1, -1])
        # self.mf = np.fliplr(np.conj(np.array(self.FSP)))
        # print(self.mf.shape)
        self.sample_buffer = np.array([],dtype=np.complex64)
        # self.output_buffer = np.zeros([],dtype=np.complex64)
        # self.mf = np.flip(np.conj(np.array(fsp,dtype=np.complex64)))
        self.filter_state = np.zeros(len(self.mf)-1,dtype=np.complex64)

    def work(self, input_items, output_items):
        #print(len(input_items[0]))
        
        self.sample_buffer = np.concatenate((self.sample_buffer, input_items[0]))
        produced = 0
        while len(self.sample_buffer) >= 3456:
            x = self.sample_buffer[:3456]
            self.sample_buffer = self.sample_buffer[3456:]
            y = np.convolve(x,self.mf,mode='full')
            y[:len(self.filter_state)] = y[:len(self.filter_state)] + self.filter_state
            output_items[0][:] = np.abs(y[:-len(self.filter_state)])
            # idx = np.argmax(output_items[0])
            self.filter_state = y[-len(self.filter_state):]
            produced += 1
            '''
            self.add_item_tag(0, # Write to output port 0
              self.nitems_written(0) + idx, # Index of the tag in absolute terms
              pmt.intern("FSP"), # Key of the tag
              pmt.from_double(np.double(1)) # output_items[0][idx])) # Value of the tag
             )
             '''
        return produced
        '''
        x = np.array(input_items[0])
        y = np.convolve(x,self.mf,mode='full')
        y[:len(self.filter_state)] = y[:len(self.filter_state)] + self.filter_state
        #print(len(y))
        #print(len(y[:-len(self.filter_state)]))
        output_items[0][:] = np.abs(y[:-len(self.filter_state)])
        idx = np.argmax(output_items[0])
        #print(len(output_items[0]))
        self.filter_state = y[-len(self.filter_state):]
        #print(self.filter_state)
        self.consume(0, len(input_items[0])) # len(x))
        self.add_item_tag(0, # Write to output port 0
          self.nitems_written(0) + idx, # Index of the tag in absolute terms
          pmt.intern("FSP"), # Key of the tag
          pmt.from_double(np.double(np.abs(y[idx]))) # output_items[0][idx])) # Value of the tag
         )
        #print(len(x),len(y),len(output_items[0]))
        return len(output_items[0])
        '''
        # For this sample code, the general block is made to behave like a sync block
        #ninput_items = min([len(items) for items in input_items])
        #noutput_items = min(len(output_items[0]), ninput_items)
        #output_items[0][:noutput_items] = input_items[0][:noutput_items]
        #self.consume_each(noutput_items)
        #return noutput_items

