clc
clear all
close all
sat=1
if sat==0
    load('mfp_deinterleave') %samples in 10880 bit frames
else
    load('mfp_deinterleave2') %samples in 10880 bit frames
end
[frames, frame_length]=size(samples);
%removing other sat
if(sat==0)
    samples(:,5:8:end)=[];
    samples(:,5:7:end)=[];
    samples(:,5:6:end)=[];
    samples(:,5:5:end)=[];
else
    samples(:,1:8:end)=[];
    samples(:,1:7:end)=[];
    samples(:,1:6:end)=[];
    samples(:,1:5:end)=[];
end
[frames, frame_length2]=size(samples);
rate=1/2;
if rate==1/3
    trellis = poly2trellis(7, [163 135 147]);
else
    if(sat==0)
        trellis = poly2trellis(7, [163 135]);
    else
        trellis = poly2trellis(7, [135 147]);
    end
end
conEnc = comm.ConvolutionalEncoder(trellis);
modBPSK = comm.BPSKModulator;
chan = comm.AWGNChannel('NoiseMethod','Signal to noise ratio (SNR)','SNR',10);
demodBPSK = comm.BPSKDemodulator('PhaseOffset',0,'DecisionMethod','Log-likelihood ratio');
vDec = comm.ViterbiDecoder(trellis);
vDec.TerminationMethod="Terminated"
vDec.ResetInputPort=1;

error = comm.ErrorRate('ComputationDelay',3,'ReceiveDelay',34);
decoded_data=[];
decoded_data2=[];
flip=-1;
for counter = 1:frames
    temp_data=zeros(1,255*8*2*2);
    for loop = 1:frame_length2/4
        if(sat==0)
            temp_data((loop-1)*6+1)=flip*samples(counter,(loop-1)*4+1);
            temp_data((loop-1)*6+3)=flip*samples(counter,(loop-1)*4+2);
            temp_data((loop-1)*6+5)=flip*samples(counter,(loop-1)*4+3);
            temp_data((loop-1)*6+6)=flip*samples(counter,(loop-1)*4+4);
        else
            if (0)
                temp_data((loop-1)*6+1)=flip*samples(counter,(loop-1)*4+1);
                temp_data((loop-1)*6+2)=flip*samples(counter,(loop-1)*4+2);
                temp_data((loop-1)*6+4)=flip*samples(counter,(loop-1)*4+3);
                temp_data((loop-1)*6+6)=flip*samples(counter,(loop-1)*4+4); 
            else
                temp_data((loop-1)*6+5)=flip*samples(counter,(loop-1)*4+1);
                temp_data((loop-1)*6+1)=flip*samples(counter,(loop-1)*4+2);
                temp_data((loop-1)*6+4)=flip*samples(counter,(loop-1)*4+3);
                temp_data((loop-1)*6+6)=flip*samples(counter,(loop-1)*4+4); 
            end
        end
    end
    %re-arrange
    %puncture effect initial state =  1, -1, -1, -1, -1,  1
    receivedBits = vDec(temp_data(1:4080)');
    decoded_data=[decoded_data;receivedBits'];
    receivedBits = vDec(temp_data(4080+1:2*4080)');
    decoded_data=[decoded_data;receivedBits'];
    %errors = error(data,receivedBits);
end
%errors(1)
%errors(2)
%decoded_data=reshape(decoded_data,2*frames,frame_length*rate/2 );
size(decoded_data)
%figure()
%spy(RS_block(:,1:8:end))