% VAD using short time energy and zero-cross rate
% created 2021/11/22 20:40:06 
clc 
clear all
close all
% close all
% aa=16/15682/4.882812500000000e-04
[x_in,Fs]=audioread('PHONE_001.wav');
% x_input=x_two(:,2);
[m,index]=max(x_in)
x_in=x_in/abs(max(x_in));%maxֵ����2.0895293����c++/2.0895=MATLAB��ֵ
x_in=x_in(1:196000);
% Tlow�ж�����������Thigh�ж��Ƿ����������
wlen=256;
inc=fix(wlen/2);
% inc=1;
wnd = hamming(wlen);
% [x_frame,t,frameNo] = cut_frame(x_in,wnd,inc); 
x_frame=cut_frame2(x_in,wlen);
% ����ZCR
[m,n]=size(x_frame);
zcr=get_zcr(x_frame,10e-3);
zcr=zcr/max(zcr);
figure;
subplot(411)
stem(zcr,'.');

energy=sum(x_frame.^2,2);%�Ƿ��Nû��ϵ��ֻȡ������ֵ
% energy=energy/max(energy);
subplot(412)
stem(energy,'.','r');
amp_l=0.02;
amp_h=0.10;%high_level
zcr_thr=0.08;
status=0;
% Ҫ�õ�ÿһ��Ƭ�ε���ʼ֡�ͽ���֡
% x_frame:291 frames, 256 samples
% ����³���Ժ�hang-overЧӦ����Ҫ���ö���״̬
frame_status=zeros(m,1);

hangover=0;
for i=1:m   
    switch status
        case{0,1}
            if energy(i)>amp_h%�����������ж�
                status=2;
            elseif energy(i)>amp_l||zcr(i)>zcr_thr%�п���
                status=1;
            else
                status=0;
            end
        case 2
            if energy(i)>=amp_h&&zcr(i)>zcr_thr%����ͬʱ�������Ϊ��������Ƭ��
                status=2;%����
                frame_status(i)=1;
            elseif energy(i)>=amp_l&&frame_status(i-1)==1
                frame_status(i)=1;
                status=2; 
            elseif zcr(i)>=zcr_thr&&frame_status(i-1)==1
                %����hangover�׶�
                frame_status(i)=1;
                status=2;               
            elseif i>=5&&frame_status(i-1)==1&&frame_status(i-2)==1&&frame_status(i-3)==1&&hangover<4
                status=2;
                frame_status(i)=1;
                hangover=hangover+1;
                if hangover==4
                    hangover=0;
                    frame_status(i)=0;
                end
            else
                frame_status(i)=0;
                hangover=0;
                status=0;
            end
            
            
    end
end
% % nop

subplot(413)
stem(frame_status,'.');
subplot(414)
plot(x_in)
hold on

x_start=zeros(size(x_frame,1),1);
x_end=zeros(size(x_frame,1),1);
j=0;
k=0;
sum=0;
for i=2:size(x_frame,1)
    if frame_status(i-1)==0&&frame_status(i)==1
        j=j+1;
        x_start(j)=i;
        sum=sum+1;
    end
    if frame_status(i-1)==1&&frame_status(i)==0
        k=k+1;
        x_end(k)=i;
    end
end

       
        
        
                
            