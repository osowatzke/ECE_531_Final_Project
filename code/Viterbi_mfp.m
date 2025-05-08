clc
clear all
close all
sat=1; % sat0=SAT1A, sat1=SAT1B, we are using SAT1B
if sat==0
    load('../data/mfp_deinterleave') %samples in 10880 bit frames
else
    load('../data/mfp_deinterleave2') %samples in 10880 bit frames
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
vDec = comm.ViterbiDecoder(trellis);
vDec.TerminationMethod="Terminated"
%vDec.ResetInputPort=1;

decoded_data=[];
flip=1; % flip to test 180 ambiguity
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
    %re-arrange for block interleave if needed
    %RS block 1
    receivedBits = vDec(temp_data(1:4080)');
    decoded_data=[decoded_data;receivedBits'];
    %RS block 2
    receivedBits = vDec(temp_data(4080+1:2*4080)');
    decoded_data=[decoded_data;receivedBits'];
end
size(decoded_data)
spy(decoded_data(:,1:200))