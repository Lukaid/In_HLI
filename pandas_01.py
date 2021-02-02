# # pandas study in hanjin logistics institute

# import pandas as pd
# #시리즈는 1차원으로 이루어진 데이터 배열, 데이터프레임은 2차원

# myList = pd.Series([1, 2, 3, 4])
# print(myList)
# # 괄호의 개수가 차원의 수

# df1 = pd.DataFrame([["wow", "friends"], [100, 200]])
# print(df1)

# df1.columns = ["qwe", "qww"]
# df1.index =df1["qwe"]

# df1["qwe"]

import pandas as pd
import numpy as np

idol = pd.read_csv("korean-idol.csv")
# pd.DataFrame(idol)

# # idol.info()
# # idol.describe() #계산이 가능한 값만 계산 해줌
# # idol.sort_index()
# # idol.sort_values(by=['키', '브랜드평판지수'])
# # idol.loc[2:5,:] # R이랑 numpy는 미만, pandas는 이하
# # idol.iloc[:, [0, 3, 6]] # iloc는 또 미만 ... ㅅㅂ
# # idol[idol['키'] > 180]
# # idol[idol['키'] > 180]['이름'] # 그 중 이름 칼럼만
# # idol.loc[idol['키'] > 180]
# # idol.loc[idol['키'] > 180, '이름'] #loc도 가능
# # my_condition = ['플레디스', 'sm']
# # idol.loc[idol['소속사'].isin(my_condition), '소속사']
# # idol.isna()
# # idol['그룹'][idol['그룹'].isna()]
# # idol['그룹'].notnull()
# # idol.loc[idol['키'].isna()]

# # for i in list(idol.columns):
# #     print(idol.loc[idol['{}'.format(i)].isna()])


# # pandas에서 행추가는 append로 dict형태로..
# idol = idol.append({'이름':'이성우', '그룹': '솔로', '소속사':'항공대', '성별': '남자', '생년월일':'1994-01-15', '키':181.0, '혈액형':'B', '브랜드평판지수':0}, ignore_index=True)
# idol.loc[idol['키'] > 180]

# pd.pivot_table(idol, index = "그룹", columns='혈액형', values='키') # 인덱스는 행, 칼럼은 열, 밸류는 값 (default는 평균)
# pd.pivot_table(idol, index='그룹', columns='혈액형', values='브랜드평판지수', aggfunc=np.mean)
# idol.head()
# idol.groupby('소속사').count() # df.groupby(원하는 칼럼).원하는 통계값()
# idol.groupby('혈액형').mean()['키']
# idol.groupby('성별')['키'].mean()
# idol.groupby('성별')['키'].count()

# # 멀티 인덱스

# df_tmp = idol.groupby(['혈액형', '성별']).mean()
# df_tmp.unstack('혈액형')
# df_tmp.reset_index() # 얘는 다시 그룹화되기 전의 데이터 프레임으로 돌려 줌


# idol['키'].fillna('') #이렇게 해도 원본파일은 안바뀌지, 다시 넣거나 replace = True
# hm = idol['키'].mean()
# idol['키'].fillna(idol['키'].mean())
# #axis = 0 -> 행 | axis = 1 -> 열
# idol.dropna(axis = 0, how='any') #how는 어떨때 날릴지 결정, any는 하나라도 있으면 날림
# idol.dropna(axis = 0, how='all') #all은 해당 row에 모든 값이 NaN일 경우만 날림

# idol['소속사'].drop_duplicates() # drop_duplicates - 중복된값 제거 - Unique - 처음 값만 유지, keep='last'로 주면 마지막꺼 남김
# idol['소속사'].drop_duplicates().count() # 유니크 한 값은 몇개?
# idol = idol.drop_duplicates() #이렇게 하면 모든 칼럼의 내용이 똑같을 때만 드랍

# idol.drop_duplicates('소속사') #얘는 데이터프레임에서 행을 제거

# idol.drop('그룹', axis = 1)

# idol_2 = pd.read_csv('korean-idol-2.csv')
# idol_2 = idol_2.append({'이름':'이성우', '연봉':'10000', '가족수':'1'}, ignore_index=True)
# idol_2

# df_tmp = pd.concat([idol, idol], sort = False) #얘는 row로 즉, 밑에 그냥 붙이는거, 합치고 싶은 df를 리스트로 줌, sort = False는 순서 안변하게 함
# df_tmp.reset_index() # 인덱스 다시 설정
# df_tmp.reset_index(drop = True) #원래 인덱스 없앰


# pd.concat([idol, idol_2], axis=1) #axis = 1은 column으로 붙이기 얘는 근데 말 그대로 붙이는거임 키값으로 붙이려면  merge

# pd.merge(idol, idol_2, on = '이름', how = 'left') #pd.merge(left, right, on = '기준칼럼' how = 붙이는 방법)
# # how에는 
# # left:왼쪽 df에 오른쪽 df 붙임 
# # right: 오른쪽df 에 왼쪽 df 붙임 
# # inner: 교집합
# # outer: 합집합
# # 없는 값은 NaN이 드감, 더 있는 값은 드랍됨

# pd.merge(idol, idol_2, left_on = '이름', right_on = '이름' how = 'outer') #기준 칼럼 이름이 다를 경우 


# idol['키'].dtype
# idol['키'].astype(int)
# idol = idol['키'].fillna(-1)

# pd.to_datetime(idol['생년월일'])

# idol.loc[idol['성별'] == '남자', '성별'] = 1 이렇게 해도 되지만
# idol.loc[idol['성별'] == '여자', '성별'] = 0

idol

idol.info()

idol.select_dtypes(include = 'object') # 문자열 만
idol.select_dtypes(exclude = 'object') # 숫자만
idol.select_dtypes(exclude = 'object') + 10 # 숫자만 뽑아서 연산
idol.select_dtypes(exclude = 'object').columns

idol[idol.select_dtypes(exclude = 'object').columns]

# 원핫인코딩 - 더미 생성

blood_map = {'A':0, 'B':1, 'O':2, 'AB':3}

idol['혈액형_code'] = idol['혈액형'].map(blood_map)
idol['혈액형_code'].value_counts()

pd.get_dummies(idol['혈액형_code'])
pd.get_dummies(idol['혈액형'], prefix='혈액형')