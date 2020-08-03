import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from tqdm import tqdm



#functions
def custom_onehot(arr):
    img = np.zeros((len(arr),4))
    for index, value in enumerate(arr):
        if value=='A':
            img[index][0] = 1
        elif value=='C':
            img[index][1] = 1
        elif value=='G':
            img[index][2] = 1
        elif value=='T':
            img[index][3] = 1

    return img.T

def save_img(img,loc,i):
    fig, ax = plt.subplots(figsize=(75,1))
    ax.imshow(img, interpolation='none', cmap='gray', aspect='auto')
    plt.axis('off')
    #plt.savefig('image.png',bbox_inches = 'tight',pad_inches=0)
    plt.savefig('data/'+str(loc)+'/'+str(loc)+'_'+str(i)+'.png',bbox_inches = 'tight',pad_inches=0)
    plt.close(fig)
    
    
    
def make_images(df,seq_type):
    #start = 
    n,m = df.shape
    data = df[seq_type].values
    for i in tqdm(range(n)):
        pos = custom_onehot(np.array(list(data[i])))
        save_img(pos,seq_type,i)

#load data

positive_df = pd.read_csv('positive_df.csv')
negative_df = pd.read_csv('negative_df.csv')
        
#before function call  
print ('started for promoter')
make_images(positive_df,'promoter')

print ('completed promoter, starting for non_promoter')

make_images(negative_df,'non_promoter')

print ('All done')


