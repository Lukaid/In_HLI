import pandas as pd
import random
from  math import pow, sqrt, ceil
from itertools import permutations
from sklearn.cluster import MiniBatchKMeans, KMeans
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError

# Table scheme define
from tbl_scheme import DROPS,CREAT,INDEX





def push_to_database(conn, df, tbl_nam):
  df.columns = [x.lower() for x in df.columns.tolist()]

  print(df.head(3))
  df.to_sql(name=tbl_nam, con=conn, if_exists='append', index=False)



def random_tml(nums=70, hubs=4, dims='100x300'):
  # This make random terminal attributes
  tml_idx = ['tml_%05d'%x for x in range(nums)]
  
  # Check imput Dims
  dim_x, dim_y = [int(x) for x in dims.split('x')]
  # Generate Uniform Scatter Location
  x_points = [random.randint(0,dim_x) for x in range(nums)]
  y_points = [random.randint(0,dim_y) for x in range(nums)]
  
  # makeTML initial information
  tml_info = [[tml_idx[x], x_points[x], y_points[x]] for x in range(len(tml_idx))]

  # find k-means cluster to assume hub
  tml_coords = [x[1:] for x in tml_info]
  k_means = KMeans(init='k-means++', n_clusters=hubs, n_init=10)
  k_means.fit(tml_coords)
  clstr_label = k_means.labels_

  # mark cluster ID on tml_info
  tml_info = [tml_info[x] + [clstr_label[x]] for x in range(len(tml_info))]

  # transform to dataframe
  df_tml = pd.DataFrame(tml_info, columns = ['TMLCOD','LONGITUDE','LATITUDE','TMLASN'])
  
  # pick a tml from TMLASN
  hubs = []
  for r in set(df_tml.TMLASN.tolist()):
    subrgn = df_tml[df_tml.TMLASN == r]
    rand_idx = random.choice(subrgn.index)
    hubs.append(rand_idx)

  # mark as hub
  for hub in hubs:
    df_tml.at[hub,'TMLTYP'] = 'hub'

  # mark as sub
  df_tml.at[list(set(df_tml.index) - set(hubs)), 'TMLTYP'] = 'sub'


  return df_tml

def random_box(tmls, ttl_amount = 1000000, typ_rate='4:3:3'):
  # this make random box attributes to as historical data even we have to aggregate in use
  box_idx = ['box_%07d'%x for x in range(ttl_amount)]

  # populate CGOTYPe by distribution
  std, lrg, etc = [int(x)/10 for x in typ_rate.split(':')]
  std_set = ['std' for x in range(int(ttl_amount*1.1 * std))]
  lrg_set = ['lrg' for x in range(int(ttl_amount*1.1 * lrg))]
  etc_set = ['etc' for x in range(int(ttl_amount*1.1 * etc))]

  potential_set = std_set + lrg_set + etc_set
  random.shuffle(potential_set)
  box_typ = random.sample(potential_set,ttl_amount)

  # populate Origin and Destination
  ## origin
  tml_lst = tmls.TMLCOD.tolist()
  orgns = random.choices(tml_lst,k=ttl_amount)
  dstns = []
  for x in orgns:
    dst = random.choice(list(set(tml_lst) - set([x])))
    dstns.append(dst)
  
  # generate all box attributes
  box_info = [[box_idx[x], box_typ[x], orgns[x], dstns[x]] for x in range(len(box_idx))]

  df_box = pd.DataFrame(box_info,columns = ['INVNUM','CGOTYP','ORGCOD','DSTCOD'])

  return df_box

def random_vcl(tmls, ttl_amount = None, typ_rate='100:1100:200:45:3', rglr_rate = 0.4):
  # Check Vehicle count
  v_TR = v_11 = v_8 = v_5 = v_2p5 = None
  rate_in = [int(x) for x in typ_rate.split(':')]
  if ttl_amount != None:
    vcl_count = ttl_amount
    rates = [x/sum(rate_in) for x in rate_in]
    v_TR, v_11, v_8, v_5, v_2p5 = [int(x*ttl_amount) for x in rates]
  else:
    vcl_count = sum(rate_in)
    v_TR, v_11, v_8, v_5, v_2p5 = rate_in


  # populate vehcle types
  VCLTYP = ['TR' for x in range(v_TR)] \
          + ['11' for x in range(v_11)] \
          + ['8' for x in range(v_8)] \
          + ['5' for x in range(v_5)] \
          + ['2.5' for x in range(v_2p5)]

  random.shuffle(VCLTYP)

  # generate vehicle ID
  VCLCOD = ['vcl_%06d'%x for x in range(vcl_count)]

  # Assign random Region
  random_region = random.choices(tmls.TMLCOD.tolist(), k=vcl_count)

  # populate vehicle info
  vcl_info = [[VCLCOD[x],VCLTYP[x],random_region[x]] for x in range(vcl_count)]
  df_vcl = pd.DataFrame(vcl_info, columns=['VCLCOD','VCLTYP','VCLORG'])
  
  # mark regular or not
  rglr_count = int(rglr_rate * vcl_count)
  rglr_idx = random.sample(df_vcl.index.tolist(), k=rglr_count)
  df_vcl.at[rglr_idx,'VCLOPS'] = 'regular'
  df_vcl.at[df_vcl[df_vcl.VCLOPS!='regular'].index,'VCLOPS'] = 'temporary'

  return df_vcl

def calc_distn(tmls, bln_directional=False, directional_err = [1,15]):
  # this generate uclidian distance between terminals 
  tml_lst = tmls.TMLCOD.tolist()
  """ populate all permutations """
  compliment_arcs = list(permutations(tml_lst,2))
    
  dist_set = []
  for org, dst in compliment_arcs:
    x1_idx = tmls[tmls.TMLCOD == org].index.tolist()[0]
    x2_idx = tmls[tmls.TMLCOD == dst].index.tolist()[0]
    x1_x, x1_y = tmls[['LONGITUDE','LATITUDE']].loc[x1_idx]
    x2_x, x2_y = tmls[['LONGITUDE','LATITUDE']].loc[x2_idx]

    calc_distance = ceil(sqrt(pow(x1_x - x2_x,2) + pow(x1_y - x2_y, 2)))
    dist_set.append(calc_distance)
  
  # the noise option gives random difference between forword and backowrd
  """gives all random to all arch """
  if bln_directional:
    dist_set = [x + random.randint(*directional_err) for x in dist_set]

  
  dist_info = [list(compliment_arcs[x]) + [dist_set[x], 'km'] for x in range(len(list(compliment_arcs)))]

  dist_df = pd.DataFrame(dist_info, columns= ['TMLFRM','TMLTTO','DISTANCE', 'UNIT'])
  return dist_df

if __name__ == '__main__':
  """
  This script generate random data and push to postgreSQL
  """
  # database connection
  acss_point = "postgresql://%s:%s@%s:%s/%s"%('pyusr', 'pybot', '10.13.1.30', '5432','netwk_anly')
  engine = create_engine(acss_point, encoding='utf-8', pool_pre_ping=True, connect_args={'connect_timeout': 28800})

  conn = engine.connect()

  # Initialize databases
  """ drop the all tables """
  for drop_qry in DROPS:
    engine.execute(drop_qry)
  """ create the all tables """
  for creat_qry in CREAT:
    engine.execute(creat_qry)
  """ gives all index on each tables """
  for index_qry in INDEX:
    engine.execute(index_qry)

  # Terminal generation
  tml = random_tml(nums=6, hubs=2, dims='100x300')

  # Demand generation
  """typ_rate = standard:large:etc"""
  box = random_box(tmls=tml, ttl_amount = 1000, typ_rate='4:3:3')

  # Vehicle generation
  """
  if ttl_amount is set, rate will be applied. otherwise, absolute values will be
  typ_rate = T/R:11T:8T:5T:2.5T 
  """
  vcl = random_vcl(tmls=tml, ttl_amount = None, typ_rate='3:4:5:0:3')


  # Distance Infomation
  dis = calc_distn(tmls=tml, bln_directional=True, directional_err = [1,15])
  
  # Cost Handling Information
  """ This Part Requires discussion for scope """

  # Cost Trucking Information
  """ This Part Requires discussion for scope """


  # push to DB
  #-- ABX_INVOICE
  push_to_database(conn = conn, df=box, tbl_nam='abx_invoice')
  
  #-- ABX_HANDLING
  #### N/A

  #-- AVX_VCL
  push_to_database(conn = conn, df=vcl, tbl_nam='avx_vcl')
  
  #-- ATM_TML
  push_to_database(conn = conn, df=tml, tbl_nam='atm_tml')
  
  #-- MCOD_MST


  # calculated Info
  # Distance CIN_DIST
  push_to_database(conn = conn, df=dis, tbl_nam='cin_dist')






  # disconnect database
  conn.close()