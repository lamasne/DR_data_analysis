function [data conditions q_loaded_fit q_unloaded_fit reso_freq_fit Rs del_Rs del_Xs] = Zsf_calculator_lorentzian_RS(folderpath,savepath,sample_name,ref_index,varargin)


%% read out s2p raw data
datapaths = dir(horzcat(folderpath,'*.s2p'));

%% create condition matrix based on the s2p names
% just some sorting of the matrix to go in the right order
for i = 1:length(datapaths)
    name_split{i} = split(datapaths(i).name,'_')';
    for j = 1:4
        name_matrix(i,j) = name_split{i}(1,j);
    end
end

%% 
for i = 1:length(name_matrix)
    num_list(i) = cellfun(@str2num,name_matrix(i,1));
end
[sorted_list index] = sort(num_list); 

name_matrix = name_matrix(index,:);

% create conditions matrix which will be returned by function

for i = 1:length(datapaths)
    usertemp_str{i,1} = char(name_matrix(i,3));
    usertemp(i,1) = str2num(usertemp_str{i,1}(3:end));
    systemp_str{i,1} = char(name_matrix(i,2));
    systemp(i,1) = str2num(systemp_str{i,1}(3:end));
    field_str{i,1} = char(name_matrix(i,4));
    field(i,1) = str2num(field_str{i,1}(2:end-5));
end
conditions = [field usertemp systemp];






%% read out the s2p files

for i = 1:length(datapaths)
     try
    data{i,1} = dlmread(horzcat(folderpath,datapaths(index(i)).name),'',5,0); %read datafiles which name is saved in 'filenames'
  catch ME
    fprintf('Readout without success: %s\n', ME.message);
    continue;  % Jump to next iteration of: for i
  end
end
fprintf("If no: previous message 'without success' then, readout worked successfully\n");


for i = 1:length(data)
    if not(isempty(data{i}))
       try
            [q_loaded(i,1) q_unloaded(i,1) reso_freq(i,1) beta_1(i,1) beta_2(i,1)] = DR_cal_Patrick(data{i});
            frequency{i} = data{i}(:,1);
            magnitude{i} = data{i}(:,4);
        catch ME
            fprintf('Readout without success: %s\n', ME.message);
        continue;  % Jump to next iteration of: for i
        end
    end
end

for i=1:length(q_loaded)
    if not(isempty(data{i}))
       try
            [q_loaded_fit(i,1) reso_freq_fit(i,1)] = lorentzian_fit_T(conditions(i,2),frequency{i},magnitude{i},q_loaded(i,1),reso_freq(i,1),savepath); % add 'plot' to arguments if you want to see the lorentzian fit
                                                                                                                                                             % add 'save' to arguments if you want to save the lorentzian fit
            q_unloaded_fit(i,1) = q_loaded_fit(i,1)*(1+beta_1(i,1)+beta_2(i,1));
        catch ME
            fprintf('Readout without success: %s\n', ME.message);
        continue;  % Jump to next iteration of: for i
        end
    end
end
%% Plotting

figure()
plot(conditions(1:length(q_loaded_fit),2),q_loaded_fit(:,1),'x-')
hold on

plot(conditions(1:length(q_unloaded_fit),2),q_unloaded_fit(:,1),'x-')
xlabel('T in K')
ylabel('Q in a.u.')
grid on
title(strcat(sample_name,' @',string(conditions(1,1)),' T'));
legend('Q_{loaded}^{lorentzian}','Q_{unloaded}^{lorentzian} ','location','best');
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('Q_vsH_lorentzian_%d',conditions(1,1)),'T.png'))


figure()
plot(conditions(1:length(reso_freq_fit),2),reso_freq_fit(:,1),'x-')
xlabel('T in K')
ylabel('f_0 in Hz')
grid on
title(strcat(sample_name,' @',string(conditions(1,1)),' T'));
legend('f_0^{lorentzian}','location','best');
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('f0_vsH_lorentzian_%d',conditions(1,1)),'T.png'))


%% calculate now the surface resistances from the Q-values
setup_factors = dlmread('C:\Users\nlamas\Desktop\workspace\DR\epsilon_all.txt','\t',0,0);

xx = 5:0.01:100;
yy_epsilon = spline(setup_factors(:,1),setup_factors(:,2),xx)';
yy_Gs = spline(setup_factors(:,1),setup_factors(:,3),xx)';
yy_losstangent = spline(setup_factors(:,1),setup_factors(:,4),xx)';

for i = 1:length(conditions(:,2))
      try
            index(i,1) = find(abs(round(conditions(i,2),1)-xx)<1e-4);
            g_factor(i,1) = yy_Gs(index(i),1);
            tan_delta(i,1) = yy_losstangent(index(i),1);  
        catch ME
            fprintf('Readout without success: %s\n', ME.message);
        continue;  % Jump to next iteration of: for i
      end  
end


for i = 1:length(q_unloaded_fit)
    Rs(i,1) = (g_factor(i)/2)* ((1/q_unloaded_fit(i)) - tan_delta(i));
end

%% calculate now the changes in surface impedance


for i = 1:length(Rs)
    [T_value T_index] = min(conditions(:,1));
    del_Rs(i,1) = Rs(i,1)-Rs(ref_index,1);
    del_Xs(i,1) = (-1)*g_factor(i,1)*((reso_freq_fit(i,1)-reso_freq_fit(ref_index,1))/(reso_freq_fit(ref_index,1)));
end

fig = figure();
plot(conditions(1:length(Rs),2),del_Rs,'x-')
hold on
plot(conditions(1:length(Rs),2),del_Xs,'x-')
grid on
title(strcat(sample_name,' @',string(conditions(1,1)),' T'));
xlabel('H in Oe')
ylabel('\Delta Z in \Omega')
legend('\Delta R_s^{lorentzian}','\Delta X_s^{lorentzian}','location','best')
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('Zsf_vsH_lorentzian_%d',conditions(1,1)),'T.png'))



%% Save calculated results in txt file

B = [conditions(1:length(q_unloaded_fit),1) conditions(1:length(q_unloaded_fit),2) q_loaded_fit(:,1) q_unloaded_fit(:,1) reso_freq_fit(:,1) Rs(:,1) del_Rs(:,1) del_Xs(:,1)];
file_ID = fopen(horzcat(savepath,sprintf('%s',sample_name),'_',sprintf('Zsf_vs_H_lorentzian_%d',conditions(1,1)),'T.txt'),'w');
fprintf(file_ID,'%1s \t%1s \t%1s \t%1s \t%1s \t%1s \t%1s \t%1s \r\n', 'field', 'Temperature', 'q_loaded', 'q_unloaded','reso_freq', 'Rsf', 'del_Rsf', 'del_Xsf' )
fprintf(file_ID,'%1d \t%1d \t%1d \t%1d \t%1d \t%1d \t%1d \t%1d \r\n',B')
fclose(file_ID);

