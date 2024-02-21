function [del_Xs_2] =  Xs_temp_correction_new(conditions,reso_freq_fit,ref_index,savepath,correction_factor)
    %% plot the temperature profile
    num = [1:length(conditions(:,2))];
    xx_num = [num(1) num(2) num(3) num(4) num(end-1) num(end)];
    yy_temp = [conditions(1,2) conditions(2,2) conditions(3,2) conditions(4,2) conditions(end-1,2) conditions(end,2)];
    yy_temp_spline = spline(xx_num(:),yy_temp(:),num)';
    yy_temp_inter = interp1(xx_num(:),yy_temp(:),num)';
    fig =figure()
    plot(num,conditions(:,2),'x-','linewidth',1.2)
    hold on
    plot(num,yy_temp_spline,'-','linewidth',1.2)
    plot(num,yy_temp_inter,'-','linewidth',1.2)
    grid on
    title(horzcat('@',num2str(conditions(1,2)),' K'))
    xlabel('{\it #} ')
    ylabel('{\itT} (K)')
    set(gca,'fontweight','bold')

    %% calculate now the surface resistances from the Q-values
    setup_factors = dlmread('Z:\Resonator\Setup_factors\setup_factors\epsilon_all.txt','\t',0,0);

    xx = 5:0.001:100;
    yy_epsilon = spline(setup_factors(:,1),setup_factors(:,2),xx)';
    yy_Gs = spline(setup_factors(:,1),setup_factors(:,3),xx)';
    yy_losstangent = spline(setup_factors(:,1),setup_factors(:,4),xx)';

    fig = figure();
    plot(setup_factors(:,1),setup_factors(:,2),'x')
    hold on
    plot(xx,yy_epsilon,'-');
    grid on
    xlabel('T in K');
    ylabel('\epsilon');
    legend('\epsilon','spline')

    fig = figure();
    plot(setup_factors(:,1),setup_factors(:,3),'x')
    hold on
    plot(xx,yy_Gs,'-');
    grid on
    xlabel('T in K');
    ylabel('G_s in \Omega');
    legend('G_s','spline')

    fig = figure();
    plot(setup_factors(:,1),setup_factors(:,4),'x')
    hold on
    plot(xx,yy_losstangent,'-');
    grid on
    xlabel('T in K');
    ylabel('tan( \delta)');
    legend('tan( \delta)','spline')

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

    for i = 1:length(num)
          try
                index_2(i,1) = find(abs(round(yy_temp_inter(i,1),3)-xx)<1e-4);
                epsilon_2(i,1) = yy_epsilon(index_2(i),1);
            catch ME
                fprintf('Readout without success: %s\n', ME.message);
            continue;  % Jump to next iteration of: for i
          end  
    end

    

    %% calculate now the changes in surface impedance

    for i = 1:length(conditions)
        del_Xs_2(i,1) = (-1)*g_factor(i,1)*(((reso_freq_fit(i,1)-reso_freq_fit(ref_index,1))/(reso_freq_fit(ref_index,1)))+(correction_factor*(epsilon_2(i)-epsilon_2(ref_index))/(epsilon_2(ref_index))));  % 0.1 factor is a correction factor which accounts for the unknown permittivity of rutile
    end

    fig = figure();
    plot(conditions(:,1),del_Xs_2,'x-')
    grid on
    xlabel('H in Oe')
    ylabel('\Delta Z in \Omega')
    legend('\Delta X_s^{lorentzian}','location','best')
    saveas(fig,horzcat(savepath,'Xs_corrected.png'))
end