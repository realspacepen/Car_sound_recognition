import numpy as np
import matplotlib.pyplot as plt
import os
import librosa
from MyVAD import mfcc, div_VAD
from EM_UBM import calculate_likelihood, unit_gaussian, GMM_train
from MAP_adapt import map_adaptation

# from model_test import calculate_likelihood # 怎么总会进入另一个模块？？因为该文件里面除了定义的函数 还有其他指令，调用之后会进入执行其他指令
# 上面这个问题要用if=main解决

car_ubm_path = 'F:/08PythonProjects/vehicle_sound_classification\VehicleSoundRaw\may_multiviolation_txt'
# car_gmm_path = 'F:/08PythonProjects/vehicle_sound_classification\VehicleSoundRaw/CUT_feb2apr_multiviolation_C01'
car_gmm_path = 'F:/08PythonProjects/vehicle_sound_classification\VehicleSoundRaw/feb2apr_multiviolation_txt'
car_data_path = 'F:/08PythonProjects/vehicle_sound_classification\car_data'
# wav_path = 'F:/08PythonProjects/vehicle_sound_classification\VehicleSoundRaw/feb2apr_multiviolation_txt'
# filename='SA1.wav'
# filepath=os.path.join(root_path,filename)

VAD_Thr = 0.05
winlen = 0.032
overlen = 0.5 * winlen
K = 12
D = 12
user_GMM_num = 3
USERNUM = 20

# 得到所有用户的UBM
# path_list = os.listdir(car_ubm_path)
# global_data = np.zeros((1, D))
# # 这部分训练UBM模型
# for car_num, sub_folders in enumerate(path_list):
#     if car_num < 30:
#         os.chdir(car_ubm_path + "/" + sub_folders)
#         path = os.getcwd()
#         ls = os.listdir(path)
#         j = 0
#         for i_file in ls:
#             if str(i_file.split('.')[-1]) == 'wav':
#                 if j <= 1:
#                     filenames = os.path.join(path, i_file)
#                     sig, sample_rate = librosa.load(filenames, sr=32000)
#                     speech_frames = div_VAD(sig, VAD_Thr, winlen, sample_rate)
#                     mfcc_vectors = mfcc(speech_frames, sample_rate, winlen, D, 512)  # 得到所有帧的MFCC,(230,12)
#                     global_data = np.append(global_data, mfcc_vectors, axis=0)
#                 j += 1
#             if j == 2:
#                 break
#     else:
#         break
# global_data = global_data[1:np.size(global_data, axis=0), :]
# # print(global_data.shape)
# GMM_train(global_data, K, 1e-20, 150, car_ubm_path)

# 开始训练每个user的GMM
# 分别用1,2,3个wav训练用户GMM，得到准确率分别为26,28,32.6%
#
# path_list=os.listdir(car_gmm_path)
# for car_nums,sub_folders in enumerate(path_list):
#     if car_nums<USERNUM:
#         user_data=np.zeros((1,D))
#         os.chdir(car_gmm_path + "/" + sub_folders)
#         path = os.getcwd()
#         ls=os.listdir(path)
#         j=0
#         for i_file in ls:
#             if str(i_file.split('.')[-1])=='wav':
#                 if j<user_GMM_num:    # use 2 wav files, from the second wav in sequence,1
#                     filenames = os.path.join(path, i_file)
#
#                     sig, sample_rate = librosa.load(filenames, sr=16000)
#                     speech_frames = div_VAD(sig, VAD_Thr, winlen, sample_rate)
#                     mfcc_vectors = mfcc(speech_frames, sample_rate, winlen, 12, 512)  # 得到所有帧的MFCC,(230,12)
#                     user_data=np.append(user_data,mfcc_vectors,axis=0)
#                 pass    # find index here!2021-7-6 17:38:18
#                 j+=1
#             if j==user_GMM_num:
#                 break
#     # print('start MAP process...')
#         map_adaptation(user_data,K,1e-20,150,10,sub_folders)
#         print(sub_folders, 'end')
#     else:
#         break

# 测试单个wav属于谁

ubm_file = os.path.join(car_ubm_path, 'ubm_file_cars.npy')
ubm = np.load(ubm_file, allow_pickle=True).item()
mu_ubm,cov_ubm,pi_ubm = ubm["mean"], ubm["cov"], ubm["pi"]
car_list=os.listdir(car_gmm_path)
wav_sum,wav_true=0,0
for i_car,sub_folders in enumerate(car_list):
    if i_car<USERNUM:
        os.chdir(car_gmm_path + "/" + sub_folders)
        wav_path=os.getcwd()
        wav_list = os.listdir(wav_path)
        k = 0
        print(sub_folders)
        for i_file in wav_list:  # 遍历文件夹寻找wav
            if str(i_file.split('.')[-1]) == 'wav':
                if (k >=user_GMM_num):  #用前3个文件进行GMM训练
                    filenames = os.path.join(wav_path, i_file)
                    sig, sample_rate = librosa.load(filenames, sr=16000)
                    speech_frames = div_VAD(sig, VAD_Thr, winlen, sample_rate)
                    test_vectors = mfcc(speech_frames, sample_rate, winlen, 12, 512)  # 得到所有帧的MFCC,(230,12)
                    # 计算测试文件的每个GMM模型下的得分，减去UBM下的似然函数
                    ls = os.listdir(car_data_path)
                    Score = np.zeros(((len(ls) - 0), 1))
                    for j, i_npy in enumerate(ls):
                        if j < 20:
                            file = os.path.join(car_data_path, i_npy)
                            gmm = np.load(file, allow_pickle=True).item()
                            mu_k = gmm["mean"]
                            cov_k = gmm["cov"]
                            pi_k = gmm["pi"]
                            Score[j, :] = calculate_likelihood(K, test_vectors, pi_k, mu_k, cov_k) - calculate_likelihood(K,test_vectors, pi_ubm, mu_ubm, cov_ubm)
                    print('USER=', int(np.argmax(Score)))
                    # 完成得分计算，取max作为识别结果
                    wav_sum+=1
                    if np.nanargmax(Score)==i_car:
                        wav_true+=1
                k += 1
    else:
        break
print("Total wav=",wav_sum," True wav=",wav_true," Rate=",wav_true/wav_sum)


