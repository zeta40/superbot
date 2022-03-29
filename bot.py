from distutils.command.config import config
from youtube_dl import cache
from telethon import TelegramClient, events, sync
import asyncio
import os
import zipfile
import re
import requests
from zipfile import ZipFile , ZipInfo 
import multiFile
import random
from bs4 import BeautifulSoup

import Client
import traceback
from config import*


links =[]

#Users_Data=[['testray11'],['testray12'],['testray13'],['testray14'],['testray15'],['testray16'],['testray17'],['testray18']]
Users_Data=[f'{USUARIO}',f'{USUARIO_ID}']
ExcludeFiles = ['bot.py','config.py','multiFile.py','Client.py','requirements.txt','Procfile','__pycache__','.git','.profile.d','.heroku','bot.session','bot.session-journal','output']

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


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size


async def upload_to_moodle(f,msg):
            #rand_user=Users_Data[random.randint(0,len(Users_Data)-1)]
            rand_user=Users_Data
            size = await get_file_size(f)
            try:
                await msg.edit(f'⚙️Subiendo...\n\n🔖Archivo: {str(f)}\n\n📦Tamaño: {sizeof_fmt(size)}')
                moodle = Client.Client(rand_user[0],f'{MOODLE_PASSWORD}')
                loged = moodle.login()
                if loged == True:
                    resp = moodle.upload_file(f,rand_user[1])
                    data=str(resp).replace('\\','')
                    await msg.edit(f'✅ Finalizado ✅')
                    await msg.delete()
                    await msg.respond(f'✅ Subido ✅\n\n🔖Archivo: {str(f)}\n📦Tamaño: {str(sizeof_fmt(size))}\n\n👤Usuario: <code>{USUARIO}</code> \n🔑Contraseña: <code>{MOODLE_PASSWORD}</code>\n🔗Enlace:\n{data}', parse_mode="html")
                    
                 
            except Exception as e:
                print(traceback.format_exc(),'Error en el upload')
                await msg.edit(f'❗️Error al Subir❗️\n💢 Hay problemas con el Moodle 💢')
                



async def process_file(file,bot,ev,msg):
    try:

        msgurls = ''
        maxsize = 1024 * 1024 * 1024 * 2
        file_size = await get_file_size(file)
        chunk_size = 1024 * 1024 * ZIP_MB
        #rand_user=Users_Data[random.randint(0,len(Users_Data)-1)]
        rand_user=Users_Data
        
        if file_size > chunk_size:
            await msg.edit(f'🛠Comprimiendo...\n\n🔖Archivo: {str(file)}\n\n📦Tamaño Total: {str(sizeof_fmt(file_size))}\n\n📚Partes de: {ZIP_MB} MB')
            mult_file =  multiFile.MultiFile(file+'.7z',chunk_size)
            zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(file)
            zip.close()
            mult_file.close()
            nuvContent = ''
            i = 0
            data=''
            for f in multiFile.files:
                await msg.edit(f'⚙️Subiendo...\n\n🔖Archivo: {str(f)}\n\n📦Tamaño Total: {str(sizeof_fmt(file_size))}\n\n📚Partes de: {ZIP_MB} MB')
                moodle = Client.Client(rand_user[0], f'{MOODLE_PASSWORD}')
                loged = moodle.login()
                if loged == True:
                    resp = moodle.upload_file(f,rand_user[1])
                    data=data+'\n\n'+str(resp).replace('\\','')
            await msg.edit(f'✅ Subido ✅\n\n🔖Archivo: {str(file)}\n📦Tamaño Total: {str(sizeof_fmt(file_size))}\n📚Partes de: {ZIP_MB}\n\n👤Usuario: <code>{USUARIO}</code>\n🔑Contraseña: <code>{MOODLE_PASSWORD}</code>\n\n🔗Enlace:\n{data}', parse_mode="html")

        else:
            await upload_to_moodle(file,msg)
            os.unlink(file)

    except Exception as e:
            await msg.edit('(Error Subida) - ' + str(e))


async def processMy(ev,bot):
    try:
        text=ev.message.text
        message = await bot.send_message(ev.chat_id, '⚙️Procesando...')
        if ev.message.file:
            await message.edit(f'⚙️Descargando Archivo...\n\n{str(ev.message.file.name)}\n\n📦Tamaño: {str(sizeof_fmt(ev.message.file.size))}')
            file_name = await bot.download_media(ev.message)
            await process_file(file_name,bot,ev,message)
    except Exception as e:
                        await bot.send_message(str(e))


async def down_mega(bot,ev,text):
    mega=Mega()
    msg = await bot.send_message(ev.chat_id,'🛠Procesando Enlace de MEGA...')
    try:
        mega.login(email= f'{GMAIL_MEGA}',password= f'{PASS_MEGA}')
    except:
        await msg.edit('❗️Error en la cuenta de MEGA❗️')
    try:    
        await msg.edit(f'⚙️Descargando...\n\n{str(text)}')
        path=mega.download_url(text)
        await msg.edit(f'D✅ Descargado {path} con éxito ✅')
        await process_file(str(path),bot,ev,msg)
    except:
        msg.edit('❗️Error en la Descarga❗️')
        print(traceback.format_exc())    

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/');
            return tokens[len(tokens)-1]
    except:
           tokens = str(url).split('/');
           return tokens[len(tokens)-1]
    return ''

def save(filename,size):
    mult_file =  multiFile.MultiFile(filename+'.7z',size)
    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()
    mult_file.close()

async def upload_to_moodle_url(msg,bot,ev,url):
    rand_user=Users_Data
    await msg.edit('⚙️Analizando...')
    html = BeautifulSoup(url, "html.parser")
    print(html.find_all('apk'))
    req = requests.get(url, stream=True, allow_redirects=True)
    if req.status_code == 200:
        try:
            chunk_size=1024 * 1024 * 49
            chunk_sizeFixed=1024 * 1024 * 49
            filename = get_url_file_name(url,req)
            filename = filename.replace('"',"")
            file = open(filename, 'wb')
            await msg.edit(f'⚙️Descargando...\n\n{str(filename)}\n\n📦Tamaño: {str(sizeof_fmt(req_file_size(req)))}')
            for chunk in req.iter_content(chunk_size=chunk_sizeFixed):
                if chunk:
                    print(file.tell())
                    file.write(chunk)
                else:
                    print('no hay chunk')    

            file.close()
            await process_file(file.name,bot,ev,msg)
        except:
            print(traceback.format_exc())            

        multiFile.files.clear()    
    pass


async def lista(ev,bot,msg):
    global links
    for message in links:
        try:
            multiFile.clear()
            clear_cache()
            text = message.message.text
            if message.message.file:
                msg = await bot.send_message(ev.chat_id,f'⚙️Descargando...\n\n{text}')
                file_name = await bot.download_media(message.message)
                await process_file(file_name,bot,ev,msg)
            elif 'mega.nz' in text:
                await down_mega(bot,ev,text)
            elif 'https' in text or 'http' in text:
                await upload_to_moodle_url(msg,bot,ev,url=text)       
        except Exception as e:
            await bot.send_message(ev.chat_id,e)
    links=[]                 

def init():
    
    try:
        
        bot = TelegramClient( 
            'bot', api_id=API_ID, api_hash=API_HASH).start(bot_token =BOT_TOKEN ) 
 
        action = 0
        actual_file = ''
    
        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
            global links
            text = ev.message.text
            file = ev.message.file
            user_id = ev.message.peer_id.user_id
            clear_cache()
            multiFile.clear()
            
            if user_id in OWNER:                
                if '#watch' in text:
                    await bot.send_message(ev.chat_id,'🕠Esperando...')
                elif '#cache' in text:
                    clear_cache()  
                elif 'mega.nz' in text:
                    #await down_mega(bot,ev,text)
                    msg= await bot.send_message(ev.chat_id,'🔗Enlace de MEGA Encontrado y añadido a procesos...\n\n /up')
                    links.append(ev)
                
                elif 'https' in text or 'http' in text:
                    msg= await bot.send_message(ev.chat_id,'🔗Enlace Encontrado y añadido a procesos...\n\n /up')
                    links.append(ev)
                elif file:
                    await bot.send_message(ev.chat_id,'📁Archivo Encontrado y añadido a procesos...\n\n /up')
                    links.append(ev)    
                elif '/up' in text:
                    msg = await bot.send_message(ev.chat_id,'❕Analizando...')
                    await lista(ev,bot,msg)
                elif '/pro' in text:
                    await bot.send_message(ev.chat_id, f'📋Procesos:\n\n{len(links)}\n\n/up')
                elif '/clear' in text:
                    await bot.send_message(ev.chat_id, f'🗑 {len(links)} Procesos Limpiados 🗑')
                    links.clear()
                elif '/start' in text:               
                    await bot.send_message(ev.chat_id,'❕Información❕\n\n❕Envíame enlaces directos o renvíame archivos.\n\n❕Para hacer una lista de descargas solo envíame todo lo que desees y luego utiliza /up para empezar a descargar todo.\n\n⚙️ Comandos ⚙️\n\n/up - Comando para iniciar una descarga o las descargas.\n/pro - Comando para mostrar una lista de procesos en pocas palabras para mostrar cuantos archivos se empezaran a subir uno atrás del otro.\n/clear - Comando para eliminar toda la lista de procesos, ojo luego de que se inicie la subida no podrás pausar así que revisa bien lo que enviaras.\n/info - Muestra información acerca de la configuración del Bot.')                 
                elif '/info' in text:
                    await bot.send_message(ev.chat_id,f'❕Información❕\n\n🔖Moodle: {MOODLE_URL}\n👤Usuario: <code>{USUARIO}</code>\n🔑Contraseña: <code>{MOODLE_PASSWORD}</code>\n📚Tamaño: {ZIP_MB}',parse_mode='HTML') 
                elif ev.message.file:
                    links.append(ev)    
                    #await processMy(ev,bot)
                elif '#clear' in text:
                    links=[]
                else: 
                    await bot.send_message(ev.chat_id,'❗️Acceso Denegado❗️')
                        

        loop = asyncio.get_event_loop() 
        loop.run_forever()
    except:
        print(traceback.format_exc())
        init()






if __name__ == '__main__': 
   init()