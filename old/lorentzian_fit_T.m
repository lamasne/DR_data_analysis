function [q_unloaded freq_reso_fit] = lorentzian_fit_T(temp,frequency,magnitude,q_loaded,reso_freq,savepath,varargin)

show_plot     = true;
save_plot     = false;
  
  k=1;
  while k <= length(varargin)
      switch varargin{k}
          case 'plot'
              show_plot = true;
          case 'save'
              save_plot = true;
      end
      k = k+1;
  end

magnitude = power(10,magnitude./20); % in linear representation

% magnitude_S11 = power(10,magnitude_S11./20); % in linear representation
% 
% magnitude_S22 = power(10,magnitude_S22./20); % in linear representation

fo = fitoptions('Method','NonlinearLeastSquares',...
               'Lower',[(max(magnitude(:,1)))-0.1 0  reso_freq(1,1)-100000000 -10 -10],...
               'Upper',[(max(magnitude(:,1)))+0.1 q_loaded(1,1)+(q_loaded(1,1)*0.01)  reso_freq(1,1)+100000000 10 10],...
               'StartPoint',[(max(magnitude(:,1))) q_loaded(1,1) reso_freq(1,1) 0 0]);  
         
ft = fittype(@(a,b,c,d,e,x) abs(a./(1+2*1i*b.*((x-c)./c))+d+1i*e),'independent',{'x'},'coefficients',{'a','b','c','d','e'},'options',fo); % determining function to fit
[fit_1,gof_1] = fit(frequency(:,1),magnitude(:,1),ft); %perform fit


% %% Prepare the second fit function
% 
% m_start = (magnitude_S11(end)-magnitude_S11(1))/(frequency(end)-frequency(1));
% 
% b_start = magnitude_S11(2)-(m_start*frequency(2));
% 
% fo_2 = fitoptions('Method','NonlinearLeastSquares',...
%                'Lower',[min(magnitude_S11) 2.5259e4-1e4  reso_freq(1,1) -10 -10 m_start b_start-100],...
%                'Upper',[max(magnitude_S11) 2.5259e4+1e4  reso_freq(1,1) 10 10 m_start b_start],...
%                'StartPoint',[(min(magnitude_S11)+max(magnitude_S11))*0.5 2.5259e4 reso_freq(1,1) 0 0 m_start b_start]);  
%          
% 
% ft_2 = fittype(@(a,b,c,d,e,m,b2,x) abs((a./(1+2*1i*b.*((x-c)./c)))+d+1i*e)+(m.*x+b2),'independent',{'x'},'coefficients',{'a','b','c','d','e','m','b2'},'options',fo_2); % determining function to fit
% [fit_2,gof_2] = fit(frequency(10:190,1),magnitude_S11(10:190,1),ft_2); %perform fit
% 
% 
% %% Prepare the third fit function
% 
% m_start_3 = (-1)*(magnitude_S22(end)-magnitude_S22(1))/(frequency(end)-frequency(1));
% 
% b_start_3 = magnitude_S22(2)-(m_start_3*frequency(2));
% 
% fo_3 = fitoptions('Method','NonlinearLeastSquares',...
%                'Lower',[min(magnitude_S22) 2.5259e4-1e4  reso_freq(1,1) -10 -10 m_start_3 b_start_3-100],...
%                'Upper',[max(magnitude_S22) 2.5259e4+1e4  reso_freq(1,1) 10 10 m_start_3 b_start_3],...
%                'StartPoint',[(min(magnitude_S22)+max(magnitude_S22))*0.5 2.5259e4 reso_freq(1,1) 0 0 m_start_3 b_start_3]);  
%          
% 
% ft_3 = fittype(@(a,b,c,d,e,m,b2,x) abs((a./(1+2*1i*b.*((x-c)./c)))+d+1i*e)+(m.*x+b2),'independent',{'x'},'coefficients',{'a','b','c','d','e','m','b2'},'options',fo_3); % determining function to fit
% [fit_3,gof_3] = fit(frequency(:,1),(-1)*magnitude_S22(:,1),ft_3); %perform fit


if (show_plot)
    for i = 1:1
        fig = figure();
        plot(frequency(:,i),magnitude(:,i),'x-','linewidth',1.2)
        hold on
        p1 = plot(fit_1,'m')
        set(p1,'lineWidth',1.2);
        grid on
%         title(strcat('Temperature:',string(temp(i)),' K'))
        dim = [.2 .5 .1 .1];
        str = {sprintf('S_M = %1.2f', fit_1.a),sprintf('Q_{L} = %1.0f', fit_1.b),sprintf('f_0 = %1.4d GHz', fit_1.c*1e-9),sprintf('S_{cR} = %1.0d', fit_1.d),sprintf('S_{cX} = %1.0d', fit_1.e)};
        annotation('textbox',dim,'String',str,'FitBoxToText','on','Fontsize',8,'LineWidth',1,...
        'backgroundcolor','w');
         xlabel('\nu (GHz)','Interpreter','tex')
        ylabel('|S_{21}|','Interpreter','tex')
        set(gca,'fontweight','bold')

    end
end
if (save_plot)
   saveas(gcf,horzcat(savepath,sprintf('lorentzian_%d',temp),'_K.png'))
   saveas(gcf,horzcat(savepath,sprintf('lorentzian_%d',temp),'_K.pdf'))
end
q_unloaded = fit_1.b;
freq_reso_fit = fit_1.c;

end

% beta_1_fit = (1-fit_2.a)/(fit_2.a+fit_3.a);
% beta_2_fit = (1-fit_3.a)/(fit_2.a+fit_3.a);