function [data, conditions, q_loaded_fit, q_unloaded_fit, reso_freq_fit, Rs, del_Rs, del_Xs] = Zsf_lorentzian_calculator(inputs_path, outputs_path, sample_name)

%% Parameters
T = 50;
f_str = '1';
ref_index = 1; % ????

inputs_path = horzcat(inputs_path, int2str(T), 'K/freq ', f_str, '/');
%% read out s2p raw data
datapaths = dir(horzcat(inputs_path, '*.s2p'));

%% create condition matrix based on the s2p names
% just some sorting of the matrix to go in the right order

split(datapaths(1).name,'_')'
name_matrix = zeros(length(datapaths), 

for i = 1:length(datapaths)
    name_split(i) = split(datapaths(i).name,'_')';
    disp(name_split(i))
    for j = 1:numel(name_split(i))
        name_matrix(i,j) = name_split(i);
    end
end
disp(name_matrix(1,:))

%% 
for i = 1:length(name_matrix)
    num_list(i) = cellfun(@str2num,name_matrix(i,1));
end
[sorted_list index] = sort(num_list); 

name_matrix = name_matrix(index,:);

% create conditions matrix which will be returned by function

for i = 1:length(datapaths)
    usertemp_str{i,1} = char(name_matrix(i,4));
    usertemp(i,1) = str2num(usertemp_str{i,1}(3:end));
    systemp_str{i,1} = char(name_matrix(i,3));
    systemp(i,1) = str2num(systemp_str{i,1}(4:end));
    field_str{i,1} = char(name_matrix(i,5));
    field(i,1) = str2num(field_str{i,1}(3:end-5));
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
  fprintf("Readout worked successfully\n");
end


for i = 1:length(data)
    if not(isempty(data{i}))
       try
            [q_loaded_fit(i,1) q_unloaded_fit(i,1) reso_freq_fit(i,1) beta_1_fit(i,1) beta_2_fit(i,1)] = DR_cal_Patrick(data{i});
            frequency{i} = data{i}(:,1);
            magnitude{i} = data{i}(:,4);
        catch ME
            fprintf('Readout without success: %s\n', ME.message);
        continue;  % Jump to next iteration of: for i
        end
    end
end

  
          beta_1_fit = zeros(length(data), 1); % Add this line
          beta_2_fit = zeros(length(data), 1); % Add this line
for i = 1:length(q_loaded_fit)
    if ~isempty(data{i}) && ~any(any(isnan(data{i}))) && ~any(any(isinf(data{i})))
        try
            % Provide initial values for the fit
            initial_values = [initial_q_loaded_value, initial_reso_freq_value]; % Replace with appropriate initial values

            % Perform the fit with initial values
            [q_loaded_fit(i,1), reso_freq_fit(i,1)] = lorentzian_fit_T(conditions(i,2), frequency{i}, magnitude{i}, initial_values, savepath);

            % Calculate q_unloaded_fit using the fitted values
            q_unloaded_fit(i,1) = q_loaded_fit(i,1) * (1 + beta_1(i,1) + beta_2(i,1));
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
title(strcat(sample_name{1},' @',string(conditions(1,1)),' T'));
legend('Q_{loaded}^{lorentzian}','Q_{unloaded}^{lorentzian} ','location','best');
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('Q_vsH_lorentzian_%d',conditions(1,1)),'T.png'))


figure()
plot(conditions(1:length(reso_freq_fit),2),reso_freq_fit(:,1),'x-')
xlabel('T in K')
ylabel('f_0 in Hz')
grid on
title(strcat(sample_name{1},' @',string(conditions(1,1)),' T'));
legend('f_0^{lorentzian}','location','best');
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('f0_vsH_lorentzian_%d',conditions(1,1)),'T.png'))


%% calculate now the surface resistances from the Q-values
setup_factors = dlmread('Z:\Resonator\Setup_factors\setup_factors\epsilon_all.txt','\t',0,0);

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
title(strcat(sample_name{1},' @',string(conditions(1,1)),' T'));
xlabel('H in Oe')
ylabel('\Delta Z in \Omega')
legend('\Delta R_s^{lorentzian}','\Delta X_s^{lorentzian}','location','best')
% saveas(gcf,horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('Zsf_vsH_lorentzian_%d',conditions(1,1)),'T.png'))



%% Save calculated results in txt file

B = [conditions(1:length(q_unloaded_fit),1) conditions(1:length(q_unloaded_fit),2) q_loaded_fit(:,1) q_unloaded_fit(:,1) reso_freq_fit(:,1) Rs(:,1) del_Rs(:,1) del_Xs(:,1)];
file_ID = fopen(horzcat(savepath,sprintf('%s',sample_name{1}),'_',sprintf('Zsf_vs_H_lorentzian_%d',conditions(1,1)),'T.txt'),'w');
fprintf(file_ID,'%1s \t%1s \t%1s \t%1s \t%1s \t%1s \t%1s \t%1s \r\n', 'field', 'Temperature', 'q_loaded', 'q_unloaded','reso_freq', 'Rsf', 'del_Rsf', 'del_Xsf' )
fprintf(file_ID,'%1d \t%1d \t%1d \t%1d \t%1d \t%1d \t%1d \t%1d \r\n',B')
fclose(file_ID);