#include <cstdint>
#include <iostream>
#include <fstream>
#include <cstring>
#include <memory>
using namespace std;
#include <math.h>
/************************************/
#define L 3886844
#define Wlen 256
#define frameNo 15183
#define SpeechNo 550
// int frameNo=L/Wlen+1;
double x_in[L];
double x_frame[15183][Wlen];
double energy[frameNo];
double zcr[frameNo];
int x_start[SpeechNo];
int x_end[SpeechNo];
int x_s;int x_e;
struct WavData{
	public:
		int16_t* data;
		long size;

		WavData(){
			data=NULL;
			size=0;
		}
};
void loadWavFile(const char* fname,WavData *ret){
	FILE* fp=fopen(fname,"rb");
	if(fp){
		char id[5];
	        int32_t size;
		int16_t format_tag,channels,block_align,bits_per_sample;
		int32_t format_length,sample_rate,avg_bytes_sec,data_size;

		fread(id,sizeof(char),4,fp);
		id[4]='\0';

		if(!strcmp(id,"RIFF")){
			fread(&size,sizeof(int16_t),2,fp);
			fread(id,sizeof(char),4,fp);
			id[4]='\0';

			if(!strcmp(id,"WAVE")){
				fread(id,sizeof(char),4,fp);
				fread(&format_length,sizeof(int16_t),2,fp);
				fread(&format_tag,sizeof(int16_t),1,fp);
				fread(&channels,sizeof(int16_t),1,fp);
				fread(&sample_rate,sizeof(int16_t),2,fp);
				fread(&avg_bytes_sec,sizeof(int16_t),2,fp);
				fread(&block_align,sizeof(int16_t),1,fp);
				fread(&bits_per_sample,sizeof(int16_t),1,fp);
				fread(id,sizeof(char),4,fp);
				fread(&data_size,sizeof(int16_t),2,fp);

				ret->size=data_size/sizeof(int16_t);
				
				ret->data=(int16_t*)malloc(data_size);
				fread(ret->data,sizeof(int16_t),ret->size,fp);
			}
			else{
				cout<<"Error: RIFF File but not a wave file\n";
			}
		}
	else{
		cout<<"ERROR: not a RIFF file\n";
	}
	}
	fclose(fp);
}

void freeSource(WavData* data){
	free(data->data);
}

int main(){
	double sum=0.0;
    int wavLength;
	float amp_l=0.02;
	float amp_h=0.10;//high_level
	float zcr_thr=0.08;
	short status=0;
	short frame_status[frameNo];
	short hangover=0;

    WavData song,song1;//song.data是一个地址，*song.data是地址里存的数
    const char* fname="PHONE_001.wav";
    loadWavFile(fname,&song);
    wavLength=song.size;//max=2380165,15682
    cout<<"length="<<wavLength<<endl;

	memset(frame_status,0,sizeof(frame_status));//YOU MUST USE memset!!!!!Otherwise,some odd value will show in the array!
	// generalize data...
	for (long i=0;i<L;i++){
        x_in[i]=song.data[i]/15682.0;	
        // cout<<x_in[i]<<',';
    }
	
	// divide frames:
	for (int i=0;i<frameNo;i++)
		{
			for(int j=0;j<Wlen;j++)
			{
				x_frame[i][j]=x_in[j+i*Wlen];
			}
		}
		// calculate zero-rate
	for (int i=0;i<frameNo;i++){
		for(int j=0;j<Wlen-1;j++){
			if(abs(x_frame[i][j]-x_frame[i][j+1])>abs( x_frame[i][j] )){
				if (abs(x_frame[i][j]-x_frame[i][j+1]>=0.01)){
					// zcr[i]=zcr[i]+1.0;
					sum=sum+1.0;
				}
			}
		}
		zcr[i]=sum/94.0;//Max_zcr=94.0
		sum=0;
	}
	// calculate energy
		for (int i=0;i<frameNo;i++)
		{
			for(int j=0;j<Wlen;j++)
			{
				sum+=x_in[j+i*Wlen]*x_in[j+i*Wlen];
			}
			energy[i]=sum;//能量不归一化方便设置阈值
			sum=0;
		}

	// judge each frame
	for (int i=0;i<frameNo;i++){
		switch (status)
		{
			case 0/* constant-expression */:
				/* code */
				if(energy[i]>=amp_h){status=2;}
				else if (energy[i]>amp_l||zcr[i]>zcr_thr){status=1;}
				else {status=0;}
				break;
			case 1:
				if(energy[i]>=amp_h){status=2;}
				else if (energy[i]>amp_l||zcr[i]>zcr_thr){status=1;}
				else {status=0;}
				break;
			case 2:
				if( energy[i]>=amp_h&&zcr[i]>=zcr_thr ){
					status=2;
					frame_status[i]=1;
				}
				else if ( energy[i]>=amp_l&&frame_status[i-1]==1){
					frame_status[i]=1;
					status=2;
				}
				else if( zcr[i]>=zcr_thr&&frame_status[i-1]==1){
					frame_status[i]=1;
					status=2;
				}
				else if( i>4&&frame_status[i-1]==1&&frame_status[i-2]==1&&frame_status[i-3]==1&&hangover<4){
					  status=2;
                	  frame_status[i]=1;
                	  hangover=hangover+1;
                	if (hangover==4){
						hangover=0;
                    	frame_status[i]=0;
					}
				}
				else{
					frame_status[i]=0;
					status=0;
					hangover=0;
				}
				break;
		default:
			break;
		}
	}

	for(int i=1;i<frameNo;i++){
		if( frame_status[i-1]==0&&frame_status[i]==1){
			
			x_start[x_s]=i;
			x_s++;
		}
		if (frame_status[i-1]==1&&frame_status[i]==0){
			
			x_end[x_e]=i;
			x_e++;
		}
	}//定义长数组出问题？？

	for(int i=1;i<frameNo;i++){
		if(frame_status[i]!=0&&frame_status[i]!=1){
			cout<<"index"<<i<<"="<<frame_status[i]<<endl;
		}
	}


    system("pause");
}