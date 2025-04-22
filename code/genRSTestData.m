% Clean workspace
clear;
clc;

% Create data
data = uint8(0:255).';
data = repmat(data,223,1);
data = data(:);

% Create Reed Solomon Encoder
enc = comm.RSEncoder(...
    'BitInput',true,...
    'CodewordLength', 255,...
    'MessageLength',  223);

% Convert data to bits
% MSB packing to match GNU radio
bits = de2bi(data,'left-msb').';

% Perform Reed Solomon Encoding
bits_enc = enc(bits(:));

% Perform modulation
data_mod = qammod(bits_enc,4,'InputType','bit');

% Typecast to single to match GNU complex format
data_mod = single(complex(data_mod));

% Packet complex data
data_packed = reshape([real(data_mod(:).'); imag(data_mod(:).')],[],1);

% Save binary data to file
fid = fopen('data_mod.dat','w');
fwrite(fid,data_packed(:),'single');
fclose(fid);

% Create read solomon decoder
dec = comm.RSDecoder(...
    'BitInput',true,...
    'CodewordLength', 255,...
    'MessageLength',  223);

% Demodulate data
data_demod = qamdemod(data_mod,4,'OutputType','bit');

% Decode data
dataDec = dec(data_demod);

% Convert data back to characters
dataDec = reshape(dataDec,8,[]);
dataDec = bi2de(dataDec.','left-msb');
dataDec = uint8(dataDec);

% Verify data is the same before and after decoding
isequal(data, dataDec)
