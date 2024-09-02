import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime as dt
import streamlit as st
import time

st.title('네이버 블로그 수집기')

def get_blog_item(url) :
    tmp = url.split("/")
    url = f'https://blog.naver.com/PostView.naver?blogId={tmp[-2]}&logNo={tmp[-1]}'
    res = requests.get(url)
    nick = tmp[-2]
    soup = BeautifulSoup(res.text, "html.parser")
    
    if soup.select_one(".se-title-text") :
        title = soup.select_one(".se-title-text").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select_one(".se-main-container").text
    else :
        title = soup.select_one(".se_title h3").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select(".se_component_wrap")[1].text
        
    title = title.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
    content = content.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
        
    return (title, nick, date, content, url)

def get_naver_blog(keyword, startdate, enddate, to_csv=False) :
    url = f"https://s.search.naver.com/p/review/48/search.naver?ssc=tab.blog.all&api_type=8&query={keyword}&start=1&nx_search_query=&nx_and_query=&nx_sub_query=&ac=0&aq=0&spq=0&sm=tab_opt&nso=so%3Add%2Cp%3Afrom{startdate}to{enddate}&prank=30&ngn_country=KR&lgl_rcode=09170128&fgn_region=&fgn_city=&lgl_lat=37.5278&lgl_long=126.9602&enlu_query=IggCADqCULjVAAAAV1mP6EPIeqVDcRO%2BjYC%2F5d2Mmgxzt%2Fj%2FMVRWVv35jMk%3D&abt=%5B%7B%22eid%22%3A%22NCO-TRIPINS%22%2C%22value%22%3A%7B%22bucket%22%3A%222%22%2C%22for%22%3A%22impression-neo%22%2C%22is_control%22%3Afalse%7D%7D%5D&retry_count=0"
    ret = []
    
    while True :
        res = requests.get(url)
        res_dic = eval(res.text)
        soup = BeautifulSoup(res_dic['contents'], 'html.parser')

        if res_dic['nextUrl'] == "" :
            break
        
        url = res_dic['nextUrl']

        for item in soup.select('.title_area > a') :
            try :
                ret.append(get_blog_item(item['href']))
            except :
                print(item['href'])

    df = pd.DataFrame(ret, columns=['title', 'nick', 'date', 'content', 'url'])
    
    if to_csv:
        df.to_csv(f"blog_{keyword}_{startdate}_{enddate}.csv", index=False)

    return df
 
with st.sidebar:
    keyword = st.text_input("검색 키워드를 입력해주세요.")
    startdate = st.date_input("조회 시작일을 선택해 주세요", dt.datetime(2024, 1, 1))
    enddate = st.date_input("조회 종료일을 선택해 주세요", dt.datetime(2024, 1, 1))
    cb_csv = st.checkbox('CSV로 저장하기')
    btn = st.button('수집하기')

if keyword and startdate and enddate and btn :
    df = get_naver_blog(keyword, startdate.strftime('%Y%m%d'), enddate.strftime('%Y%m%d'), cb_csv)
    st.dataframe(df)


