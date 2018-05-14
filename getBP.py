
def getBrandAndProduct(outputFile):
    import json
    import csv 
    import re
    import jieba
    #將產品詞庫轉成list 
    ########################尚未斷出純英文

    fn_prod = './urcosme_data/product.csv'
    with open(fn_prod, encoding = 'utf8') as csvFile:
        csvReader_product = csv.reader(csvFile)
        product = list(csvReader_product)

    #取出純字串
    product_str = []
    for i in range(len(product)):
        product_str.append(product[i][0])

    product_one = []
    #取出 EX: 菁萃亮妍能量精露(水潤型)
    for i in range(len(product_str)):
        product_one.append(re.match(u"[\u4e00-\u9fa5]+\W[\u4e00-\u9fa5]+\W",product_str[i]))

    #取出 EX: 水潤透白活感平衡液WA   
    for i in range(len(product_str)):
        product_one.append(re.match(u"[\u4e00-\u9fa5]+\w+",product_str[i]))   

    #取出 EX: 薰衣草淨白微晶去角質霜EX(傳明酸)  
    for i in range(len(product_str)):
        product_one.append(re.match(u"[\u4e00-\u9fa5]+\w+\S[\u4e00-\u9fa5]\S+",product_str[i]))    


    #取出 EX: 乳油木護手霜 Shea Butter Hand Cream 中 乳油木護手霜
    for i in range(len(product_str)):
        product_one.append(re.match(u"[\u4e00-\u9fa5]+",product_str[i]))


    #取出 EX: 芯美顏 滲透露
    for i in range(len(product_str)):
        product_one.append(re.match("[\u4e00-\u9fa5]+\s[\u4e00-\u9fa5]+",product_str[i]))   

    #取出 EX: 深層潔淨2合1潔顏泡泡霜    
    for i in range(len(product_str)):
        product_one.append(re.match("[\u4e00-\u9fa5]+\s[\u4e00-\u9fa5]+",product_str[i]))    

    #取出 EX: AHA柔膚深層潔淨卸妝乳   
    for i in range(len(product_str)):
        product_one.append(re.match("\w+[\u4e00-\u9fa5]+",product_str[i]))        


    product_two = []   
    for j in range(len(product_one)):
        if type(product_one[j])!= str and product_one[j] != None:
            product_two.append(product_one[j].group())    

    #去除不需要斷詞  
    product_list = [] 
    for j in range(len(product_two)):    
        if product_two[j] != "肌" and product_two[j] !="傳明酸" and product_two[j] !="玻尿酸" and product_two[j] !="白":
            product_list.append(product_two[j])    


    #刪除重複產品
    product_list =list(set(product_list))
    
    #將品牌詞庫轉成list
    #中文品牌名
    fn_ch = './urcosme_data/brand_CH.csv'
    with open(fn_ch, encoding = 'utf8') as csvFile:
        csvReader_brand = csv.reader(csvFile)
        brand = list(csvReader_brand)



    #去除空list,不能用remove去[],index會往前移,所以會報(index out of the range) 
    x = []
    for i in range(len(brand)):
        if brand[i] != []:
            x.append(brand[i])
        else:
            continue    

    #取出純字串    
    brand_list = []
    for i in range(len(x)):
        brand_list.append(x[i][0].replace("&",""))    

    #刪除重複品牌
    brand_list = list(set(brand_list))


    ###################################################################################


    #英文品牌名

    fn_en = './urcosme_data/brand_en.csv'
    with open(fn_en, encoding = 'utf8') as csvFile:
        csvReader_brand_en = csv.reader(csvFile)
        brand_en = list(csvReader_brand_en)

    #去除空list,不能用remove去[],index會往前移,所以會報(index out of the range) 
    y = []
    for i in range(len(brand_en)):
        if brand_en[i] != []:
            y.append(brand_en[i])
        else:
            continue    

    #取出純字串   
    brand_en_list = []
    for i in range(len(y)):
        brand_en_list.append(y[i][0].replace("&","").replace("ONE",""))

    #刪除重複品牌
    brand_en_list = list(set(brand_en_list))

    with open(outputFile,"r", encoding = 'utf8')as f:
         word = f.readlines()
    #以空白鍵切割
    words = []
    for c in range(len(word)):
        words.append(word[c].split(" "))

    #取出list中的list
    content_n = []
    for a in range(len(words)):
        for b in range(len(words[a])):
            content_n.append(words[a][b])
    content_n = [c.replace("<","(").replace(">",")").replace("》",")") for c in content_n]

    #去除字串前後字元        
    content_list = []
    for c in range(len(content_n)):
        content_list.append(content_n[c].strip().strip("、").strip("\ufeff").strip("「").strip("」"))
        #針對雅漾產品處理
        for i in range(len(content_list)):
            if content_list[i][0:2]=="雅漾":
                content_list.append(content_list[i].replace("雅漾",""))


    content_break = []
    content_break02 = [] 

    for i in range(len(content_list)):
        #正則表達式去除數字，得到match物件
        content_break.append(re.match('\D+',content_list[i]))
        #正則表達式取得中英字串(未分開) 的中文字串，得到list物件
        content_break02.append(re.findall(u'[\u4e00-\u9fa5]+',content_list[i]))

    #取出斷完物件
    content_all = []   
    for j in range(len(content_break)):
        if content_break[j] != None:
            content_all.append(content_break[j].group())

    for j in range(len(content_break02)): 
        if content_break02[j] != []:
            for i in range(len(content_break02[j])):
                content_all.append(content_break02[j][i])

    #轉成list的產品詞庫對應使用者的檔案 
    return_sql = {}
    product_start = []
    for f in range(len(product_list)):
        for g in range(len(content_all)):
            if content_all[g] == product_list[f]:
                product_start.append(product_list[f])
                #print(product_list[f])


    #判斷取出長度最大的產品名  
    try:            
        if len(product_start) > 1:       
            return_sql["product"] = max(product_start, key=len)
        else:
            return_sql["product"] = product_start[0]
    except:
        #print("NO product")
        return_sql["product"] =""    

    #品牌使用jieba斷詞
    #encoding=utf-8
    jieba.load_userdict(fn_ch)
    jieba.load_userdict(fn_en)
    jieba.load_userdict(fn_prod)

    content = open(outputFile,"r", encoding = 'utf8').read()

    #針對Olay處理
    if "Olay" in content:
        content=content.upper()

    #因品牌名稱有080，因此去掉0800等字串
    if "0800-" in content:
        content=content.replace("0800","")

    #避免辨識不成功，去掉08000等字串   output9 
    if "08000-" in content:
        content=content.replace("08000","")  

    #避免辨識不成功，去掉13M等字串    output9 
    if "13M" in content:  
        content=content.replace("13M","")    

    words_brand = list(jieba.cut(content, cut_all=False))   


    return_sql["brand"] = ""

    return_sql["brand_en"] = ""

    #轉成list的品牌詞庫對應使用者的檔案  

    #中文品牌  
    for d in range(len(words_brand)):
        for e in range(len(brand_list)):

                #針對台灣萊雅產品處理
                if words_brand[d] == "台灣萊雅":
                    return_sql["brand"] = words_brand[d].replace("台灣萊雅","巴黎萊雅")                     

                elif return_sql["brand"] == "" and words_brand[d] == brand_list[e]:
                     return_sql["brand"] = words_brand[d]               

    #英文品牌                
    for d in range(len(words_brand)):               
        for j in range(len(brand_en_list)): 

                if return_sql["brand_en"] == "" and words_brand[d] == brand_en_list[j]:
                    return_sql["brand_en"] = words_brand[d]


    return return_sql

