import pandas as pd
import streamlit as st
import datetime
import numpy as np
from calendar import monthrange
import matplotlib.pyplot as plt
from PIL import Image
#from utils.injection import inject_logo

st.set_page_config(page_title = "Relatório PDT", page_icon = Image.open('img/logo-evcomx.png'), layout="wide")

#inject_logo('img/Gerdau_logo_(2011).svg.png', 'Perdas-Térmicas')

# CSS to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

def transform_tmedpims(df):
    df.loc[df['tmedpims']>750,'tmedpims'] = df['tmedpims']-df['temperaturaobjetivada']
    return df

def get_date(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%m/%d/%Y')

def date_to_datetime(datetime_str):
    datetime_str = datetime_str.replace(" 00:00:00","")
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d')

def clean_zeros(datetime_str):
    return datetime_str.replace(" 00:00:00","")

def color(df):
    out = pd.DataFrame(None, index=df.index, columns=df.columns)
    out['tmedpims'] = (df['tmedpims']
                    .between(df['t_min'], df['t_max']) 
                    .map({True: 'background-color: lime',False: 'background-color: red'})
                    )
    return out

def color2(df):
    out = pd.DataFrame(None, index=df.index, columns=df.columns)
    out['Atendimento'] = (df['Atendimento']
                    .between(75,100) 
                    .map({True: 'background-color: lime',False: 'background-color: red'})
                    )
    return out

def set_style_row(r, sub=[]):
    if r.name in sub:
        return np.where(r>75, "background-color: lime", "background-color: red")
    return [''] * len(r)

def get_month_index(df,month,year="2022"):
    month_index = []
    for i in range(len(df)):
        if '{}-{}'.format(year,month) in df['data'].values[i]:
            month_index.append(i)
        elif '{}/{}'.format(month,year) in df['data'].values[i]:
            month_index.append(i)      
    return month_index

    
df = pd.read_csv("tb_relatorio.csv")
df_tmedpims = pd.read_csv("new_database.csv",sep=';',decimal=',')[['corrida','tmedpims']]
df = pd.merge(df,df_tmedpims,on='corrida').apply(pd.to_numeric, errors='ignore')
df = transform_tmedpims(df).dropna(subset='tmedpims')
df['tmedpims'] = df['tmedpims'].round(0)

df_tab2 = df.copy()

tab1, tab2, tab3 = st.tabs(["Histórico de Corridas", "ICs de Temperatura", "Histograma"])

with tab1:

    today = datetime.date.today()
    year = today.strftime("%Y")

    d_i = st.sidebar.date_input("Data Inicial", value=get_date('01/01/{}'.format(year)), min_value=get_date('01/01/2021'), max_value=today)
    d_f = st.sidebar.date_input("Data Final", value=today, min_value=d_i, max_value=today)

    quality = st.sidebar.text_input("Filtrar Qualidade")

    st.sidebar.markdown("Posição no Sequencial")
    col1,col2 = st.sidebar.columns(2)
    primeiras = col1.checkbox("Primeiras")
    ultimas = col2.checkbox("Últimas")

    st.sidebar.markdown("Seção")
    col1,col2 = st.sidebar.columns(2)
    s155 = col1.checkbox("155")
    s240 = col2.checkbox("240")

    st.sidebar.markdown("Tipo Sequenciamento")
    col1,col2 = st.sidebar.columns(2)
    normal = col1.checkbox("Normal" )
    mixing = col2.checkbox("Mixing" )
    col1,col2 = st.sidebar.columns(2)
    flying = col1.checkbox("Flying" )
    sem_flying = col2.checkbox("Sem Flying" )

    pan_list = list(df.panela.astype(int).sort_values().unique())
    pan_list.insert(0, "Todas as Panelas")

    dtr_list = list(df.distribuidor.astype(int).sort_values().unique())
    dtr_list.insert(0, "Todas os Distribuidores")


    pan = st.sidebar.selectbox("Panela", pan_list) 
    dtr = st.sidebar.selectbox("Distribuidor", dtr_list)

    
    d_i=datetime.datetime.fromordinal(d_i.toordinal())
    d_f=datetime.datetime.fromordinal(d_f.toordinal())
    df = df[(df['data'].apply(date_to_datetime)>=d_i)&(df['data'].apply(date_to_datetime)<=d_f)]

    df['data'] = df['data'].apply(clean_zeros)

    if quality:
        if quality.lower() in [qualidade.lower() for qualidade in df.qualidade.unique()]:
            df = df[df['qualidade'].apply(str.lower)==quality.lower()]
        else:
            st.warning("Qualidade não encontrada.")
    
    secao = []
    tipo_sequenciamento = []
    seq_pos = []

    if s155:
        secao.append(155)
    if s240:
        secao.append(240)
    if secao:
        df = df[df['secao'].isin(secao)]

    if normal:
        tipo_sequenciamento.append('Normal')
    if mixing:
        tipo_sequenciamento.append('Mixing c/a anterior')
    if flying:
        tipo_sequenciamento.append('Flying')
    if sem_flying:
        tipo_sequenciamento.append('Sem Flying')
    
    if tipo_sequenciamento:
        df = df[df['tiposequenciamento'].isin(tipo_sequenciamento)]

    if primeiras and ultimas:
        df = df[(df['sequencia']==1)|(df['sequencia']==df['sequenciatotal'])]
    elif primeiras:
        df = df[df['sequencia']==1]
    elif ultimas:
        df = df[(df['sequencia']!=1)&(df['sequencia']==df['sequenciatotal'])]

    if pan != "Todas as Panelas":
        df = df[df['panela']==pan]

    if dtr != "Todas os Distribuidores":
        df = df[df['distribuidor']==dtr]

    features_to_show = 'corrida,qualidade,data,hrvazamento,panela,fundo,distribuidor,secao,seq,tiposeq,toneis,t_obj,v_obj,tav,t_min,t_max,tmedpims'.split(',')
    df = df.rename(columns={'tiposequenciamento':'tiposeq','velocidadeobjetivada':'v_obj','temperaturaobjetivada':'t_obj'})
    

    df['seq'] = df['sequencia'].astype(str)+"/"+df['sequenciatotal'].astype(str)

    #st.dataframe(df[features_to_show].style.format({"panela":"{:.0f}","fundo":"{:.0f}","toneis":"{:.0f}","v_obj":"{:.0f}","t_min":"{:.0f}","t_max":"{:.0f}","tmedpims":"{:.1f}"}).apply(color, axis=None),unsafe_allow_html=True,height = 900)

    #st.write(df[features_to_show].style.format({"panela":"{:.0f}","fundo":"{:.0f}","toneis":"{:.0f}","v_obj":"{:.0f}","t_min":"{:.0f}","t_max":"{:.0f}","tmedpims":"{:.1f}"}).hide_index().apply(color, axis=None).to_html(), unsafe_allow_html=True,height = 900)

    st.write(df[features_to_show].style.format({"panela":"{:.0f}","fundo":"{:.0f}","toneis":"{:.0f}","v_obj":"{:.0f}","t_min":"{:.0f}","t_max":"{:.0f}","tmedpims":"{:.1f}"}).hide(axis="index").apply(color, axis=None).to_html(), unsafe_allow_html=True,height = 900)
    
    
with tab2:

    col1,col2 = st.columns(2)

    current_year = datetime.date.today().year
    current_month = datetime.date.today().month

    year = []
    c=0
    while True:
        year.append(2021+c)
        if 2021+c == current_year:
            break
        c+=1
    month = [ '01',  '02',  '03',  '04',  '05',  '06',  '07',  '08',  '09', '10', '11', '12']

    data = []
    for i in year:
        for j in month:
            if i == current_year:
                if int(j) > current_month:
                    pass
                else:
                    data.insert(0,str(i)+"/"+str(j))
            else:
                data.insert(0,str(i)+"/"+str(j))

    y_m = col1.selectbox("Carregar Mês",data)
    y,m = y_m.split("/")

    df_tab2 = df_tab2.reset_index(drop=True)
    index = []
    for i in range(len(df_tab2)):
        if '{}-{}'.format(y,m) in df_tab2['data'].values[i]:
            index.append(i)
        elif '{}/{}'.format(m,y) in df_tab2['data'].values[i]:
            index.append(i) 
    df_tab2['data'] = df_tab2['data'].apply(clean_zeros)
    df_month = df_tab2.loc[index].sort_values(by='corrida').copy().reset_index(drop=True)


    for i in range(len(df_month['data'].values)):
        if '-' in df_month['data'].iloc[i]:
            df_month.loc[i,'day'] = int(df_month['data'].iloc[i][-2:])
        elif '/' in df_month['data'].iloc[i]:
            df_month.loc[i,'day'] = int(df_month['data'].iloc[i][:2])


    df_month = df_month.dropna(subset=['tmedpims'])

    num_days = monthrange(int(y), int(m))[1]

    atendimento = pd.DataFrame(None,columns=['Corridas','Corridas OK','Frias','Quentes','Atendimento'])

    lst_atendimento = []


    for day in range(1,num_days+1):
        
        df_day = df_month[df_month['day']==day]
        df_correct = df_day[(df_day['tmedpims']>=df_day['t_min']) & (df_day['tmedpims']<=df_day['t_max'])]

        if len (df_day) > 0:

            atendimento.loc['Dia '+str(day),'Corridas'   ] = len(df_day)
            atendimento.loc['Dia '+str(day),'Corridas OK'] = len(df_correct)
            atendimento.loc['Dia '+str(day),'Frias'      ] = len(df_day[(df_day['tmedpims']<df_day['t_min'])])
            atendimento.loc['Dia '+str(day),'Quentes'    ] = len(df_day[(df_day['tmedpims']>df_day['t_max'])])
            atendimento.loc['Dia '+str(day),'Atendimento'] = np.round(100*len(df_correct)/len(df_day),2) #"{}%".format(np.round(100*len(df_correct)/len(df_day),2))
            lst_atendimento.append([day,100*len(df_correct)/len(df_day)])
    
            
    st.write(atendimento.transpose().style.apply(set_style_row, axis=1, sub=['Atendimento']).format(formatter="{:.2f}%", subset=pd.IndexSlice[['Atendimento'], :]) )

    lst_atendimento = np.array(lst_atendimento)

    fig,ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Atendimento a Temperaturas Diário - Mês de {}/{}".format(y,m))
    ax.plot(lst_atendimento[:,0],lst_atendimento[:,1])
    ax.scatter(lst_atendimento[:,0],lst_atendimento[:,1])
    plt.xticks(lst_atendimento[:,0])
    plt.ylim(0,110)
    ax.plot([0,np.max(lst_atendimento[:,0])+1],[75,75], c='red', linestyle='--')

    col1,col2 = st.columns(2)

    col1.pyplot(fig)

    fig,ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Atendimento a temperatura Mensal - Últimos 12 meses")
    ax.plot(lst_atendimento[:,0],lst_atendimento[:,1])
    ax.scatter(lst_atendimento[:,0],lst_atendimento[:,1])
    plt.xticks(lst_atendimento[:,0])
    plt.ylim(0,110)
    ax.plot([0,np.max(lst_atendimento[:,0])+1],[75,75], c='red', linestyle='--')


    kpis = {"n_runs":[],"acc":[],"month":[]}
    time=[i.split("/") for i in data[:12]]

    df_tab2['data'] = df_tab2['data'].apply(clean_zeros)

    for i in range(1,len(time)+1):
        y = time[-i][0]
        m = time[-i][1]

        index = []


        for j in range(len(df_tab2)):
            if '{}-{}'.format(y,m)   in df_tab2['data'].values[j]:
                index.append(j)
            elif '{}/{}'.format(m,y) in df_tab2['data'].values[j]:
                index.append(j) 

        
        df_month = df_tab2.loc[index].sort_values(by='corrida').copy().reset_index(drop=True)

        kpis["acc"].append(len(df_month[(df_month['tmedpims']>=df_month['t_min'])&(df_month['tmedpims']<=df_month['t_max'])])/len(df_month))
        kpis["n_runs"].append(len(df_month))
        kpis["month"].append(m+"/"+y)

    df_kpi=pd.DataFrame(kpis)
    df_kpi=df_kpi[["month","n_runs","acc"]]
    x_axis = np.arange(len(df_kpi))

    f, ax = plt.subplots(figsize=(12,8))
    ax.plot(df_kpi["acc"]*100)
    ax.scatter(x_axis,100*df_kpi["acc"].values,marker="x",c="red")
    ax.set_xticks(x_axis,df_kpi["month"].values)
    for i,metric in enumerate(df_kpi["acc"]):
        ax.annotate(        text=np.round(100*metric,2) ,xy=(x_axis[i],100*metric+0.5)   )
    ax.plot([0,11],[75,75], c='red', linestyle='--')

    plt.ylim(65,95)
    ax.set_title('Atendimento a temperatura Mensal - Últimos 12 meses')

    col2.pyplot(f)


with tab3:
   st.markdown(" # Em Breve")