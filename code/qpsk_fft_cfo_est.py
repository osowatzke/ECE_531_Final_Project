"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

from gnuradio import gr
import numpy as np
import pmt # for message strobe to send to signal source



class qpsk_fft_cfo_est(gr.basic_block):
    """
    All-in-One QPSK FFT-Based CFO Estimator

    Input: Complex stream (QPSK baseband samples)
    Output: Float stream (estimated frequency offset in Hz)

    Internally:
    - Raises signal to 4th power
    - Chunks into FFT-sized vectors
    - Applies FFT
    - Estimates frequency of peak tone (divided by 4)
    """

    def __init__(self, samp_rate=1e6, fft_size=1024):
        gr.basic_block.__init__(
            self,
            name="QPSK FFT CFO Estimator (All-in-One)",
            in_sig=[np.complex64],
            out_sig=[np.float32, (np.float32, fft_size)]
        )
        self.message_port_register_out(pmt.intern("freq_msg"))
        self.fft_size = fft_size
        self.samp_rate = samp_rate
        self.freqs = -np.fft.fftshift(np.fft.fftfreq(self.fft_size, d=1.0 / self.samp_rate))

        # Buffer to accumulate input samples
        self.sample_buffer = np.array([], dtype=np.complex64)
        #self.buffer_idx = 0

    def general_work(self, input_items, output_items):
        #global CFO_freq
        in0 = input_items[0]
        freq_est = output_items[0]
        out = output_items[1]

        produced = 0

        # Append incoming samples to buffer
        # self.sample_buffer[self.buffer_idx] = in0
        
        self.sample_buffer = np.concatenate((self.sample_buffer, in0))

        # Process while we have at least fft_size samples
        while len(self.sample_buffer) >= self.fft_size and produced < len(freq_est):
            # Take fft_size samples
            segment = self.sample_buffer[:self.fft_size]
            self.sample_buffer = self.sample_buffer[self.fft_size:]

            # Raise to the 4th power
            x4 = segment ** 4

            # Apply FFT
            fft_result = np.fft.fftshift(np.fft.fft(x4))
            #print(fft_result.shape)
            fft_result_dB = 10*np.log10(np.real(fft_result*np.conjugate(fft_result))/self.fft_size)
            #print(fft_result_dB[0])
            #print(fft_result_dB.shape)
            #print(fft_result[0])
            #out[:] = [1]*self.fft_size
            #out[:] = [-20]*self.fft_size
            out[:] = fft_result_dB
            #print(len(out))
            #print(out[0])

            # Estimate frequency from peak
            mag = np.abs(fft_result)
            peak_index = np.argmax(mag)
            est_freq = self.freqs[peak_index] / 4.0  # divide due to 4th power

            freq_est[produced] = est_freq
            produced += 1

        # Tell scheduler how many input items we used
        self.consume(0, len(in0))
        msg = pmt.to_pmt({'freq': produced})
        self.message_port_pub(pmt.intern("freq_msg"), msg)
        return min(produced,self.fft_size)

