function [Qloaded Qunloaded resonance1 beta1 beta2] = DR_cal_Patrick (data)

[MaxVarName1,Index1]=max(data(:,4));
resonance1 = data(Index1,1);

frequency1 = data(:,1);
magnitude1 = data(:,4);
magnitude1 = magnitude1 - max(magnitude1);% Normalise to maximum

indmax1 = find(magnitude1 == max(magnitude1));

f1 = interp1(magnitude1(1:indmax1), frequency1(1:indmax1), -3.01);
f2 = interp1(magnitude1(indmax1:end), frequency1(indmax1:end), -3.01);
BW1 = f2 - f1;

Qloaded = resonance1/BW1;

magnitudeS11 = data(:,2);
magnitudeS11 = magnitudeS11 - ((magnitudeS11(1)+magnitudeS11(end))*0.5);

magnitudeS22 = data(:,8);
magnitudeS22 = magnitudeS22 - ((magnitudeS22(1)+magnitudeS22(end))*0.5);

S11res = 10^(min(magnitudeS11)/20);
S21res = 10^(max(data(:,4))/20);
S22res = 10^(magnitudeS22(Index1)/20);

S11resdb = min(magnitudeS11);
S21resdb = max(data(:,4));
S22resdb = magnitudeS22(Index1);
beta1 = (1-S11res)/(S11res+S22res);
beta2 = (1-S22res)/(S11res+S22res);

Qunloaded = Qloaded*(1+beta1+beta2);