
# coding: utf-8
#!/usr/bin/python3

from __future__ import print_function
import httplib2
import os
import io

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from flask import Flask, render_template, request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from getBP import getBrandAndProduct
from werkzeug import secure_filename
try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Python OCR'
app = Flask(__name__)

#DB connection
app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql+pymysql://cosmetic:Mysqlpn102!@192.168.56.101/CosmeticDB'
db = SQLAlchemy(app)
class urcosmeTest(db.Model):
    __tablename__ = 'urcosmeTest'
    id = db.Column('id', db.Integer, primary_key = True)
    brand_EN = db.Column(db.Text)
    brand_CH = db.Column(db.Text)
    product = db.Column(db.Text)
    score = db.Column(db.Float)

def __init__(self, brand_EN, brand_CH, product,score):
    self.brand_EN = brand_EN
    self.brand_CH = brand_CH
    self.product = product
    self.score = score
    
#取得憑證
def get_credentials():
  """取得有效的憑證
     若沒有憑證，或是已儲存的憑證無效，就會自動取得新憑證

     傳回值：取得的憑證
  """
  credential_path = os.path.join("./", 'google-ocr-credential.json')
  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatibility with Python 2.6
      credentials = tools.run(flow, store)
    print('憑證儲存於：' + credential_path)
  return credentials

  
#def is_imag(filename):
    #return filename.endswith(".png") or filename.endswith(".jpg") 
  
def main(imgfile):    
  # 取得憑證、認證、建立 Google 雲端硬碟 API 服務物件
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('drive', 'v3', http=http)

  
  #imgfile = is_imag
  file = imgfile[:-4]
  # 輸出辨識結果的文字檔案
  txtfile = file+'.txt'

  # 上傳成 Google 文件檔，讓 Google 雲端硬碟自動辨識文字
  mime = 'application/vnd.google-apps.document'
  res = service.files().create(
    body={
      'name': imgfile,
      'mimeType': mime
    },
    media_body=MediaFileUpload(imgfile, mimetype=mime, resumable=True)
  ).execute()

  # 下載辨識結果，儲存為文字檔案
  downloader = MediaIoBaseDownload(
    io.FileIO('./output/'+txtfile, 'wb'),
    service.files().export_media(fileId=res['id'], mimeType="text/plain")
  )
  done = False
  while done is False:
    status, done = downloader.next_chunk()

  # 刪除剛剛上傳的 Google 文件檔案
  service.files().delete(fileId=res['id']).execute()



@app.route('/')
def upload():
   return render_template('index.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      filenames = os.listdir(".")
      for filename in filenames:
        if filename.endswith(".png") or filename.endswith(".jpg"):
          imgfile = filename
      if os.path.exists(imgfile):
        main(imgfile)
        os.remove(imgfile)
        return 'ok'
        #return redirect(url_for('show_score'))
      else:
        return "imgfile dosen't exists."

@app.route('/show_score')
def show_score():
    outputDir = "./output/"
    outputFile = outputDir + os.listdir(outputDir)[0] 
    BP = getBrandAndProduct(outputFile)
    #刪除文件檔
    if os.path.exists(outputFile):
      os.remove(outputFile)

    #回傳品牌、產品和評價分數
    try:
      if BP['product'] == "":
          return render_template('noProduct.html')
      elif BP['brand'] =="":
          ur = urcosmeTest.query.filter(urcosmeTest.brand_EN == BP['brand_en'],urcosmeTest.product.like(BP['product']+'%')).all()
          return render_template('showScore.html',  
                                brand=ur[0].brand_EN+" "+ur[0].brand_CH,
                                product =ur[0].product,
                                score = ur[0].score)
      elif BP['brand_en'] =="":
          ur = urcosmeTest.query.filter(urcosmeTest.brand_CH == BP['brand'],urcosmeTest.product.like(BP['product']+'%')).all()
          return render_template('showScore.html',
                                brand=ur[0].brand_EN+" "+ur[0].brand_CH,
                                product =ur[0].product,
                                score = ur[0].score)
      else:
          ur = urcosmeTest.query.filter(urcosmeTest.brand_EN == BP['brand_en'],urcosmeTest.brand_CH == BP['brand'],urcosmeTest.product.like(BP['product']+'%')).all()
          return render_template('showScore.html',
                                brand=ur[0].brand_EN+" "+ur[0].brand_CH,
                                product =ur[0].product,
                                score = ur[0].score)
    except:
      return render_template('noProduct.html')

if __name__ == '__main__':
  db.create_all()
  app.run(debug = True)
  

