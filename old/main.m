close all;
clear all;
opengl software;

%% 
inputs_path = 'inputs/';
outputs_path = 'outputs/';
sample_name = "FF DR001";

%% Calculating Zsf

[data, conditions, q_loaded_fit, q_unloaded_fit, reso_freq_fit, Rs, del_Rs, del_Xs] = Zsf_lorentzian_calculator(inputs_path, outputs_path, sample_name); 


%%
close all
Xs = Xs_temp_correction(conditions,reso_freq_fit,1,savepath_3{i});

%% plotting field sweeps 60K
close all
k = 1;
range_1 = 1:152;
range_2 = 153:309;

% 
fig =figure()
plot(conditions(range_1,1),reso_freq_fit(range_1),'x-','linewidth',1.2)
hold on
plot(conditions(range_2,1),reso_freq_fit(range_2),'x-','linewidth',1.2)
grid on
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
xlabel('{\itH} (Oe)')
ylabel('{\itf_0} (Hz)')
set(gca,'fontweight','bold')
legend('ramping up','ramping down')
saveas(fig,horzcat(savepath_3{k},'f0_vs_H_fit.png'))
saveas(fig,horzcat(savepath_3{k},'f0_vs_H_fit'))

%%
close all
fig =figure()
plot(conditions(range_1,1),q_loaded_fit(range_1),'x-','linewidth',1.2)
hold on
plot(conditions(range_2,1),q_loaded_fit(range_2),'x-','linewidth',1.2)
plot(conditions(range_1,1),q_unloaded_fit(range_1),'x-','linewidth',1.2)
plot(conditions(range_2,1),q_unloaded_fit(range_2),'x-','linewidth',1.2)
grid on
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
set(gca,'fontweight','bold')
xlabel('{\itH} (Oe)')
ylabel('{\itQ} (a.u.)')
legend('Q_{loaded} ramping up','Q_{loaded} ramping down','Q_{unloaded} ramping up','Q_{unloaded} ramping down','Location','best')
saveas(fig,horzcat(savepath_3{k},'Q_vs_H.png'))
%%
fig = figure()
plot(conditions(range_1,1),Rs(range_1),'x-','linewidth',1.2)
hold on
plot(conditions(range_2,1),Rs(range_2),'x-','linewidth',1.2)
grid on
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
xlabel('{\itH} (Oe)')
ylabel('{\itR_{s}} (\Omega)')
set(gca,'fontweight','bold')
% ylim([0 1e-3])
xlim([0 10e4])
legend('ramping up','ramping down','no joint','one joint','four joints remounted','location','best')
saveas(fig,horzcat(savepath_3{k},'Rs_vs_H.png'))
saveas(fig,horzcat(savepath_3{k},'Rs_vs_H'))

%%
fig =figure()
plot(conditions(range_1,1),del_Xs(range_1)-del_Xs(range_1(1)),'x-','linewidth',1.2)
hold on
plot(conditions(range_2,1),del_Xs(range_2)-del_Xs(range_1(1)),'x-','linewidth',1.2)

grid on
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
set(gca,'fontweight','bold')
xlabel('{\itH} (Oe)')
ylabel('{\it\Delta Xs} (\Omega)')
legend('ramping up','ramping down','location','Southeast')
saveas(fig,horzcat(savepath_3{k},'del_Xs_vs_H_fit.png'))
saveas(fig,horzcat(savepath_3{k},'del_Xs_vs_H_fit'))


%% plot S2P files
b = range_2(end);
fig = figure()
plot(data_S2P{range_1(1)}(:,1),data_S2P{range_1(1)}(:,2),'x-','linewidth',1.2)
hold on
plot(data_S2P{range_1(end)}(:,1),data_S2P{range_1(end)}(:,2),'x-','linewidth',1.2)
plot(data_S2P{b}(:,1),data_S2P{b}(:,2),'x-','linewidth',1.2)
grid on
set(gca,'fontweight','bold')
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
xlabel('{\itf} (Hz)')
ylabel('{\itS_{11}} (dB)')
legend('ramping up 0T','9T','ramping down 0T','location','Southeast')
saveas(fig,horzcat(savepath_3{k},'S11vsf.png'))

fig = figure()
plot(data_S2P{range_1(1)}(:,1),data_S2P{range_1(1)}(:,4),'x-','linewidth',1.2)
hold on
plot(data_S2P{range_1(end)}(:,1),data_S2P{range_1(end)}(:,4),'x-','linewidth',1.2)
plot(data_S2P{b}(:,1),data_S2P{b}(:,4),'x-','linewidth',1.2)
grid on
set(gca,'fontweight','bold')
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
xlabel('{\itf} (Hz)')
ylabel('{\itS_{21}} (dB)')
legend('ramping up 0T','9T','ramping down 0T','location','Southeast')
saveas(fig,horzcat(savepath_3{k},'S21vsf.png'))

fig = figure()
plot(data_S2P{range_1(1)}(:,1),data_S2P{range_1(1)}(:,8),'x-','linewidth',1.2)
hold on
plot(data_S2P{range_1(end)}(:,1),data_S2P{range_1(end)}(:,8),'x-','linewidth',1.2)
plot(data_S2P{b}(:,1),data_S2P{b}(:,8),'x-','linewidth',1.2)
grid on
set(gca,'fontweight','bold')
title(horzcat('@',num2str(conditions(range_1(1),2)),' K'))
xlabel('{\itf} (Hz)')
ylabel('{\itS_{22}} (dB)')
legend('ramping up 0T','9T','ramping down 0T','location','Southeast')
saveas(fig,horzcat(savepath_3{k},'S22vsf.png'))