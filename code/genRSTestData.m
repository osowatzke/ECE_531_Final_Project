% Clean workspace
clear;
clc;

% Specify whether to add errors
add_errors = true;

% Random number generator seed
rng(0);

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

% Add random errors to input data of data
if add_errors

    % Number of errors to generate
    num_errors = 15;

    % Reshape bits into a matrix
    bits_enc = reshape(bits_enc,255*8,[]);

    % Specify the bytes indices for random errors
    error_idx = randi([0 254],num_errors,size(bits_enc,2));

    % Corrupt all bits in bytes
    error_idx = reshape(error_idx,num_errors,[],size(error_idx,2));
    error_idx = 8*error_idx + (1:8);
    error_idx = reshape(error_idx,[],size(error_idx,3));

    % Apply errors
    for i = 1:size(error_idx,2)
        bits_enc(error_idx(:,i),i) = randi([0 1], size(error_idx,1), 1);
    end
    
    % Reshape back into a vector
    bits_enc = bits_enc(:);
end

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
