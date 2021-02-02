import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
print(pd.__version__)

shp = pd.read_csv("seoul_house_price.csv")
shp.info()
shp.head()

shp = shp.rename(columns = {'분양가격(㎡)' : '분양가격'}) # 변수명 재정의

shp.describe() # #계산 가능한 통계값을 추출해줌

#shp['분양가격'].astype(int)


#shp['분양가격'] = shp['분양가격'].astype(int) # '  ' 이 있다고 에러를 반환 따라서 공백 없애줘야 함
shp.loc[shp['분양가격'] == '  ']
shp['분양가격'] = shp['분양가격'].str.strip() # 공백이 제거 됨
shp.loc[shp['분양가격'] == '', '분양가격'] = 0
shp['분양가격'] = shp['분양가격'].fillna(0)
shp['분양가격'] = shp['분양가격'].str.replace(',', '')
shp['분양가격'] = shp['분양가격'].str.replace('-', '')
shp['분양가격'] = shp['분양가격'].fillna(0)
shp.loc[shp['분양가격'] == '', '분양가격'] = 0

shp['분양가격'] = shp['분양가격'].astype(int)

(shp['분양가격'] == 0).value_counts()

shp['규모구분'].str.replace('전용면적', '')

shp.info()

shp.groupby('지역명')['분양가격'].mean()

idx = shp.loc[shp['분양가격'] < 100].index # 분양가격이 100보다 작은 행의 인덱스를 추출

shp_1 = shp.drop(idx, axis = 0)

shp_1.info()
shp_1.groupby('지역명')['분양가격'].mean()
shp_1.groupby('지역명')['분양가격'].count()
shp_1.groupby('지역명')['분양가격'].max()
shp_1.groupby('연도')['분양가격'].mean()

pd.pivot_table(shp_1, index = '연도', columns = '규모구분', values='분양가격')

shp_1.groupby(['연도', '규모구분'])['분양가격'].mean()
pd.DataFrame(shp_1.groupby(['연도', '규모구분'])['분양가격'].mean())

shp_1['분양가격'].plot(kind = 'hist')
#shp_1.groupby(['연도', '규모구분'])['분양가격'].mean().plot(kind = 'hist')

plt.show()