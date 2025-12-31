import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

################################################

### Read data ###

# Big dataset
filename = '../data/cleaned/cleaned_dataset_v3.csv'
df = pd.read_csv(filename,delimiter=',')

##################################################################

df.drop(df.columns[0], axis=1, inplace=True)  # Unnamed

df.drop(columns=['url','locality','sale_type','price_per_m2','log_price_m2','cluster'], inplace=True)

##################################################################

if(1):
    df_dummies = df.copy()
    
    df_dummies.drop(columns=['property_type','property_subtype','has_open_fire'], inplace=True)

    for col in df_dummies.select_dtypes(include='object').columns:
        df[col] = df[col].fillna("None")

    
    for col in df_dummies.columns.tolist():
        if df_dummies[col].dtype == 'object' and col != 'property_id':
            dummies = pd.get_dummies(df_dummies[col], prefix=col, dummy_na=True)
            df_dummies = df_dummies.drop(columns=[col]).join(dummies)
            
    
    for col in df.columns:
        if df[col].dtype == 'object' and col != 'property_id':
            # Create dummy-columns
            dummies = pd.get_dummies(df[col], prefix=col, dummy_na=True)
            # Delete orig.column and add dummies columns
            df_dummy = df.drop(columns=[col]).join(dummies)
    
    df_dummies.drop(columns=['property_id'], inplace=True)

    print( df_dummies.dtypes )

##################################################################

if(1):
    corr_matrix = df_dummies.corr()
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(30, 30))
    sns.heatmap(corr_matrix, annot=True)
    #sns.heatmap(corr_matrix, annot=False)
    
    plt.savefig("corr_matrix_2.png", dpi=70)
    
    #plt.show()

##################################################################




##################################################################

#print( df.head(3).transpose() )

#print( df.dtypes )

#print('\n\n\n')



##################################################################

print('The job have done')

