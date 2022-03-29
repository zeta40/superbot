import traceback
from zipfile import ZipFile , ZipInfo 
import zipfile
import re

from telebot.types import Message
import Client
import telebot
import zlib
import os
import requests
import random
import youtube_dl
import multiFile
import multivolumefile as mulzip
from config import*


# ESTAS VARIABLES NO SE TOCAN
MOODLE_USER = 'testray2'
MOODLE_PASS = 'Lala*1234'


Users_Data=[['testray21','18808'],['testray22','18809'],['testray23','18810'],['testray24','18811'],['testray25','18812'],['testray26','18913'],['testray27','18814'],['testray28','18815'],['testray29','18816'],['testray30','18817']]
ExcludeFiles = ['bot.py','multiFile.py','Client.py','requirements.txt','Procfile','__pycache__','.git','.profile.d','.heroku','bot.session','bot.session-journal','output']

bot = telebot.TeleBot(BOT_TOKEN)

conf = ''

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if ExcludeFiles.__contains__(f):
                    print('-----Archivo protegido de cache clear')
                else:
                    print('Borrando'+f)
                    os.remove(f)
        return True            
    except Exception as e:
        print(str(e))
        return False

def get_url_file_name(url, req):
    name = ''
    try:
        if "Content-Deposition" in req.headers.keys():
            return str(re.findall('filename(.+)', req.headers['Content-Deposition'])[0])
        else:
            tokens = str(url).split('/')
            return tokens[len(tokens)-1]
    except:
            tokens = str(url).split('/')
            return tokens[len(tokens)-1]
    return name


def save(filename,size):
    mult_file =  multiFile.MultiFile(filename+'.7z',size)
    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()
    mult_file.close()
    print(multiFile.files)



def get_youtube_info(url):
    yt_opt = {
        'no_warnings':True,
        'ignoreerrors':True,
        'restrict_filenames':True,
        'dumpsinglejson':True,
        'format':'best[protocol=https]/best[protocol=http]/bestvideo[protocol=https]/bestvideo[protocol=http]'
              }
    ydl = youtube_dl.YoutubeDL(yt_opt)
    with ydl:
        result = ydl.extract_info(
            url,
            download=False # We just want to extract the info
        )
    return result

def filter_formats(formats):
    filter = []
    for f in formats:
        if '(DASH video)' in f['format']: continue
        if f['ext'] == 'mp4':
            if f['acodec'] =='mp4a.40.2':
                 filter.append(f)
    return filter




def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size





def save_url(url,req):
    src = get_url_file_name(url,req)
    save_dir='env'
    downloaded_file = bot.download_file(url)
    with open(save_dir + "/" + src, 'wb') as new_file:
        new_file.write(downloaded_file)  
    return save_dir + "/" + src                                 

def upload_to_moodle_yutu(url,filename, id):
    req = requests.get(url, stream=True, allow_redirects=True)
    rand_user=Users_Data[random.randint(0,len(Users_Data))]
    if req.status_code == 200:
        filename = filename
        file = open(filename, 'wb')
        msg = bot.send_message(id,'⚙️Descargando...'+ filename)
        for chunk in req.iter_content(chunk_size=1024 * 1024 * 100):
            if chunk:
                print(file.tell())
                file.write(chunk)
                
                

        file.close()
        save(filename=filename,size=1024*1024*100)
        moodle = Client.Client(rand_user[0],MOODLE_PASS)
        loged = moodle.login()
        if loged:
            data=''
            for f in multiFile.files:
                data=data+str(moodle.upload_file(f,rand_user[1])).replace('\\','')+'\n\n'
                moodle.delete_files(rand_user[1])
                bot.send_message(id,f'✅ Parte subida con éxito ✅')                
            bot.send_message(id,f'✅ Archivo Subido ✅\n\n🔗Enlace:\n\n{data}')


        else:
            bot.send_message(id,'❗️No se pudo iniciar sesión❗️')
        multiFile.files.clear()    
    pass

def upload_to_moodle(url, id):
    bot.send_message(id,'🛠Analizando...')
    req = requests.get(url, stream=True, allow_redirects=True)
    rand_user=Users_Data[random.randint(0,len(Users_Data))]
    if req.status_code == 200:
        chunk_size=1024 * 1024 * 200
        chunk_sizeFixed=1024 * 1024 * 100
        filename = get_url_file_name(url,req)
        file = open(filename, 'wb')
        msg = bot.send_message(id,'⚙️Descargando...'+ filename)
        for chunk in req.iter_content(chunk_size=chunk_sizeFixed):
            if chunk:
                print(file.tell())
                file.write(chunk)

        file.close()
        try:
            moodle = Client.Client(rand_user[0],MOODLE_PASS)
            loged = moodle.login()
        except:
            bot.send_message(id,f'❗️No se completo el inicio de sesión con: {rand_user[0]}')
            upload_to_moodle(url,id)    
        if get_file_size(filename)>chunk_size:

            save(filename=filename,size=chunk_size)
            
            if loged:
                data=''
                for f in multiFile.files:
                    data=data+str(moodle.upload_file(f,rand_user[1])).replace('\\','')+'\n\n'
                    moodle.delete_files(rand_user[1])
                    bot.send_message(id,f'✅ Parte subida con éxito ✅')                
                bot.send_message(id,f'✅ Archivo Subido ✅\n\n📦Archivo: {filename}\n\n👤Usuario: {rand_user[0]}\n🔑Contraseña: Jj1482005.',parse_mode='markdown')
                bot.send_message(id,f'🔗Enlace:\n\n{data}')


            else:
                bot.send_message(id,'❗️No se pudo iniciar sesión❗️')
        else:
            if loged:
                data=str(moodle.upload_file(filename)).replace('\\','')
                moodle.delete_files()
                bot.send_message(id,f'✅ Parte subida con éxito ✅')                
                bot.send_message(id,f'✅ Archivo Subido ✅\n\n📦Archivo: {filename}',parse_mode='markdown')
                bot.send_message(id,f'🔗Enlace:\n\n{data}')
            else:
                bot.send_message(id,'❗️No se pudo iniciar sesión❗️')    

        multiFile.files.clear()    
    pass

def upload_to_moodle_docu(file,size, id):
    multiFile.clear()
    filename=file
    file_size = size
    print(filename , file_size)
    chunk_size = 1024 * 1024 * 99
        
    bot.send_message(id,'🛠Comprimiendo...')
    mult_file =  multiFile.MultiFile(filename+'.7z',chunk_size)
    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()
    mult_file.close()
    moodle = Client.Client(MOODLE_USER,MOODLE_PASS)
    loged = moodle.login()
    if loged:
        data=''
        for f in multiFile.files:
            data=data+str(moodle.upload_file(f)).replace('\\','')+'\n\n'
            moodle.delete_files()
            bot.send_message(id,f'✅ Parte subida con éxito ✅')
        bot.send_message(id,f'✅ Archivo Subido ✅\n\n🔗Enlace:\n\n{data}')

            


    pass

@bot.message_handler(commands=['yt'])
def yutu(message):
    url = message.text.split(' ',1)[1]

    try:

        result =  get_youtube_info(url)
        formats = filter_formats(result['formats'])
        format = formats[-1]
        videofile = result['title']+ '.mp4'        
        upload_to_moodle_yutu(format['url'],videofile,message.from_user.id)
    except Exception as e:
        print(e)    

@bot.message_handler(commands=['li'])
def link(message):
    link=message.text.split(' ',1)[1]
    upload_to_moodle(url=link,id=message.from_user.id)


@bot.message_handler(commands=['cac'])
def link(message):
    if clear_cache():
        bot.send_message(message.from_user.id,'Cache borrado!')


@bot.message_handler(func=lambda m: True)
def listen(message):
    if message.text.__contains__('https') or message.text.__contains__('http'):
        upload_to_moodle(url=message.text,id=message.from_user.id)   
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def docu(message):    
        bot.send_message(message.from_user.id,f'⚙️Descargando...')
        try:
            print(message)

            '''
            file_name = message.document.file_name
            file_id = message.document.file_name
            file_id_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)
            upload_to_moodle_docu(file_name,size=file_id_info.file_size,id=message.from_user.id)
            '''
        except:
            bot.send_message(message.from_user.id,'El archivo debe ser menor de 20mb')
            print(traceback.format_exc())    

def inicio_bot():
    

    if BOT_TOKEN:

        print('-------------------------\nBot iniciado uwu\n------------------------')

        
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
 


if __name__ == '__main__':inicio_bot()