# -*- coding: utf-8 -*-

'''
prompt("Title", document.title);
var direct_url = n.src.split("?")[0].replace("/master.m3u8", "");
prompt("url", direct_url);
'''

'''
function xhrPost(url,data,callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(xhr.readyState==4){
            if ((xhr.status >= 200 && xhr.status < 300) || xhr.status == 304) {
                callback(null,xhr.responseText);
            }else{
                callback([xhr.status,xhr.responseText],null);
            }
        }
    }
    xhr.open('post',url);
    xhr.setRequestHeader('Content-Type','text/plain')
    xhr.send(data);
}
var direct_url = n.src.split("?")[0].replace("/master.m3u8", "");
xhrPost('http://127.0.0.1:13496/',JSON.stringify({name:document.title,url:direct_url}),(e,d)=>console.log(e,d))
'''

# from http://zhaouv.net/treefile/?standard_server.py

import json
import socket
import threading
import os
import time
import mimetypes
#strtime=time.strftime("%Y%m%d%H%M%S")

import sys
if(sys.version_info.major==2):
    import codecs
    open=codecs.open

def runnow_threading(func):
    out = threading.Thread(target=func)
    out.start()
    return lambda:out

def mecho(a):
    return
    print(a)

def sysecho(a):
    print(a)
    return
    @runnow_threading
    def fprint(a):
        with open('a.out','a') as fid:
            fid.write(a+'\n')

class g:
    strtemplate='HTTP/1.0 302 Move temporarily\r\nContent-Length: 0\r\nLocation: {urlstr}\r\n\r\n' #{urlstr}
    ip='127.0.0.1'
    port=13496


def initdata():
    pass

def mainget(urlstr):
    return (403,'403')


def mainpost(urlstr,body):
    callback=lambda:0
    if urlstr == '/':
        sysecho(''.join([
            'POST / ',addr[0],':',str(addr[1]),' ',str(body)
            ]))
        obj=json.loads(body)
        os.system(f"python dl_hls.py '{obj['name']}' '{obj['url']}'")
        return (200,'succeed',callback)

    return (403,'no service this url')


def mainparse(header,body):
    callback=lambda:0
    for _tmp in [1]:
        if header[:3]=='GET':
            urlstr=header.split(' ',2)[1]
            host=header.split('Host: ',1)[1].split('\r\n',1)[0]
            mainre = mainget(urlstr)
            if len(mainre)==2:
                header,body=mainre
            else:
                header,body,callback=mainre
            break

        if header[:4]=='POST':
            urlstr=header.split(' ',2)[1]
            mainre =  mainpost(urlstr,body)
            if len(mainre)==2:
                header,body=mainre
            else:
                header,body,callback=mainre
            break

        if header=='':
            header,body= (403,'')
            break

        header,body= (403,'')
    
    if hasattr(body,'encode'):
        body=body.encode('utf-8')
    if type(header)==int:
        codeDict={200:'200 OK',302:'302 Move temporarily',403:'403 Forbidden',404:'404 Not Found'}
        header=('HTTP/1.0 {statu}\r\nContent-Type: text/json; charset=utf-8\r\nContent-Length: '.format(statu=codeDict[header])+str(len(body))+'\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
        #Access-Control-Allow-Origin: null : to test in chrome
    header=header.encode('utf-8')
    return (header,body,callback)

def tcplink(sock, addr):
    mecho('\n\nAccept new connection from %s:%s...' % addr)

    tempbuffer = ['']
    data=''
    header=''
    body=''
    while True:
        # 1k most one time:
        d = sock.recv(512)
        if d:
            d=d.decode('utf-8')
            tempbuffer.append(d)
            if False: # not boolcheck:
                sock.close()
                mecho('Connection from %s:%s closed.' % addr)
                return

            tempend=tempbuffer[-1][-4:]+d
            if '\r\n\r\n' in tempend:
                headend=True
                data=''.join(tempbuffer)
                header, body = data.split('\r\n\r\n', 1)
                if header[:3]=='GET':
                    tempbuffer=[]
                    break
                tempbuffer=[body]
                a=int(header.split('Content-Length:',1)[1].split('\r\n',1)[0])-len(body.encode('utf-8'))#str.len not equal byte.len
                while a>0:
                    tempbuffer.append(sock.recv(min(a,512)).decode('utf-8'))
                    a=a-min(a,512)
                break
        else:
            break
    mecho('recv end\n===')
    body = ''.join(tempbuffer)
    mecho(header)
    mecho('---')
    if len(body)>250:
        mecho(body[:100])
        mecho('...\n')
        mecho(body[-100:])
    else:
        mecho(body)

    callback=lambda:0
    if True: 
        try:
            header,body,callback=mainparse(header,body)
        except Exception as ee:
            initdata()
            raise ee
        mecho('===\nsend start\n')
        sock.send(header)
        sock.send(body)
        mecho('\nsend end\n===')
    sock.close()
    mecho('Connection from %s:%s closed.' % addr)
    callback()

if __name__ == '__main__':

    initdata()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((g.ip, g.port))

    s.listen(500)
    sysecho('Waiting for connection...')

    
    while True:
        sock, addr = s.accept()
        t = threading.Thread(target=tcplink, args=(sock, addr))
        t.start()
