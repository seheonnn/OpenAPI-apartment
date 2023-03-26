# 아파트 거래 내역

# https://www.data.go.kr/data/15058747/openapi.do
import numpy as np
import requests
import xmltodict
import json
import matplotlib.pyplot as plt
import pandas as pd

# 그래프 한글 사용
from matplotlib import font_manager, rc
rc('font',family ='AppleGothic')

# 지역이름 -> 법정동코드 변환 코드
def searchLawdCd(locate_nm):
    raw = pd.read_csv('./dongCode.txt', sep="\t", encoding="CP949")
    realdata = raw[raw['폐지여부'] == '존재']
    strcode = realdata['법정동코드'].astype(str).apply(lambda x: x[:5])
    lawd_cd = strcode[realdata['법정동명'] == locate_nm].values[0]
    return lawd_cd

data = {
    '아파트이름' : [],
    '연도' : [],
    '평균거래금액' : [],
}
def printApartTransaction(dongCode, apartName, sDate, eDate):
    url = 'http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade'
    LAWD_CD = dongCode # LAWD_CD는 법정동 코드 10자리 중 5자리
    # DEAL_YMD = sDate # 해당 월부터 1년

    # apartName = apartName # 아파트 이름
    DATE = []
    deal = []
    avgDeal = []

    for i in range(sDate, eDate):

        if i % 100 > 12:
            i = (int(i/100) + 1) * 100 + int('{0:02d}'.format((i%100)%12))
            if i%100 == 0:
                i = int(i/100) * 100 + 12
            DEAL_YMD = str(i)
        else:
            DEAL_YMD = str(i)

        data.get('아파트이름').append(apartName)
        DATE.append(DEAL_YMD)
        data.get('연도').append(DEAL_YMD)
        print("=======================================================================")
        print(DEAL_YMD[:4] + '년' + DEAL_YMD[4:] + '월')
        params ={'serviceKey' : 'GpHkMo6DWA2mcDd7OWQuStcVgZ+WjtRLNAcfBC6sgnghQrgGi48vHixwmvhy1+AlRgDZiclDBdglJj8F7EmNsw==', 'LAWD_CD' : LAWD_CD, 'DEAL_YMD' : DEAL_YMD }

        response = requests.get(url, params=params)
        dict_data = xmltodict.parse(response.text)
        json_data = json.dumps(dict_data, ensure_ascii=False)
        # print(json_data)

        d = dict_data['response']['body']['items']['item']
        deal_m = []

        for j in range(len(d)):
            for k in d[j].keys():
                if d[j].get('아파트') == apartName:
                    amount = int(d[j].get('거래금액').replace(',', ''))
                    deal.append(amount)
                    deal_m.append(amount)
                    print(k, d[j].get(k))
                # print(k, d[i].get(k))
            # print("\n")

        deal_m = np.array(deal_m)

        avgDeal.append(np.mean(deal_m))

        # print(deal_m)

        if int(DEAL_YMD) == eDate:
            break

    data.get('평균거래금액').extend(avgDeal)
    avgDeal = np.nan_to_num(avgDeal)
    # print(avgDeal)
    # print(DATE)
    deal = np.array(deal)
    print(apartName, "평균 거래금액: ", np.mean(deal))

    # ======================= nan, 0 처리 =======================
    for i in range(1, len(avgDeal)):
        if avgDeal[i] == 0:
            avgDeal[i] = avgDeal[i-1]

    # 날짜별 거래금액
    plt.plot(DATE, avgDeal, label=apartName)





dongCode = searchLawdCd('충청남도 천안시 서북구 불당동')
print(dongCode)

plt.figure()

printApartTransaction(dongCode, '불당아이파크', 202101, 202212)
printApartTransaction(dongCode, '동일하이빌', 202101, 202212)
printApartTransaction(dongCode, '대동다숲', 202101, 202212)
printApartTransaction(dongCode, '천안불당지웰더샵', 202101, 202212)
printApartTransaction(dongCode, '불당호반써밋플레이스센터시티', 202101, 202212)

# print(data)
df = pd.DataFrame(data, index=data['연도']) # index추가할 수 있음
df.to_excel('apart_deal_info.xlsx', index=False)
# print(df)

plt.xticks(rotation=90)
plt.xlabel('날짜')
plt.ylabel('거래금액')
plt.legend()
plt.show()

