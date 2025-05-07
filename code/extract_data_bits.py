#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 gr-xm_module author.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr

class extract_data_bits(gr.basic_block):
    """
    docstring for block extract_data_bits
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="extract_data_bits",
            in_sig=[(np.complex64,3456)],
            out_sig=[(np.float32,5440)])

        self.sample_buffer = np.array([],dtype=np.complex64)
        self.fsp_count = 0
        
    def general_work(self, input_items, output_items):
        
        max_symbols_per_fsp = 3424
        
        num_bits_out = len(output_items[0]) * 5440
        num_symbols_out = num_bits_out / 2
        
        desired_symbols = max(num_symbols_out - len(self.sample_buffer), 0)
        
        num_fsps = int(np.ceil(desired_symbols/max_symbols_per_fsp))
        num_fsps = min(num_fsps, len(input_items[0]))
         
        for i in range(num_fsps):
            self.fsp_count += 1
            num_items = 3424
            if self.fsp_count == 205:
                num_items -= 160
                self.fsp_count = 0
            input_data = input_items[0][i][32:32+num_items]
            self.sample_buffer = np.concatenate((self.sample_buffer, input_data))
        
        produced = 0
        while ((len(self.sample_buffer) >= 2720) and (produced < len(output_items[0]))):
            output_items[0][produced][:] = self.sample_buffer[0:2720].view(np.float32)
            self.sample_buffer = self.sample_buffer[2720:]
            produced += 1
            
        self.consume(0, num_fsps)
        return produced

