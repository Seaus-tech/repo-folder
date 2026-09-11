import os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

# 1. FIX: Use a local folder on your Mac instead of Linux absolute /mnt/data
OUT = "./output"
os.makedirs(OUT, exist_ok=True)

W,H,FPS=960,540,24

# 2. FIX: Use a relative filename for the logo. Place the logo image in the same directory!
LOGO_FILENAME = "a_clean_high_resolution_vector_3d_glossy_logo_on.png"
logo=Image.open(LOGO_FILENAME).convert("RGBA").crop(
    Image.open(LOGO_FILENAME).convert("RGBA").getbbox()
)
logo=logo.resize((330,330),Image.Resampling.LANCZOS)

# 3. FIX: Redirect the Linux fonts to native macOS system font paths
font=ImageFont.truetype("/System/Library/Fonts/Supplemental/HelveticaNeue-Bold.ttf", 44)
small=ImageFont.truetype("/System/Library/Fonts/Supplemental/HelveticaNeue.ttf", 17)

def make_frames(kind,dur):
    root=os.path.join(OUT,"seaus_"+kind+"_frames")
    os.makedirs(root,exist_ok=True)
    n=int(dur*FPS)

    # precompute blurred logo once
    logo_glow=logo.getchannel("A").filter(ImageFilter.GaussianBlur(16))

    for i in range(n):
        t=i/FPS
        yy,xx=np.mgrid[0:H,0:W]
        cx,cy=W/2,H*0.46
        r=np.sqrt(((xx-cx)/W)**2+((yy-cy)/H)**2)
        v=np.clip(1-r*1.7,0,1)

        if kind=="console":
            arr=np.zeros((H,W,3),dtype=np.uint8)
            arr[...,0]=(3+6*v).astype(np.uint8)
            arr[...,1]=(5+9*v).astype(np.uint8)
            arr[...,2]=(11+18*v).astype(np.uint8)
        else:
            arr=np.zeros((H,W,3),dtype=np.uint8)
            arr[...,0]=(11+20*v).astype(np.uint8)
            arr[...,1]=(13+23*v).astype(np.uint8)
            arr[...,2]=(18+29*v).astype(np.uint8)

        frame=Image.fromarray(arr,"RGB").convert("RGBA")
        d=ImageDraw.Draw(frame)

        # orbital lines
        ang=t*(1.3 if kind=="console" else 0.45)
        rx,ry=(235,120) if kind=="console" else (215,110)
        for off in (0,math.pi):
            pts=[]
            for k in range(101):
                th=k/100*2*math.pi
                x=cx+rx*math.cos(th); y=cy+ry*math.sin(th)
                ca,sa=math.cos(ang+off),math.sin(ang+off)
                dx,dy=x-cx,y-cy
                pts.append((cx+dx*ca-dy*sa,cy+dx*sa+dy*ca))
            d.line(pts,fill=(230,245,255,100 if kind=="console" else 65),
                   width=4 if kind=="console" else 2)

        # bright orbit point
        a=-ang+1.0
        px=cx+rx*math.cos(a); py=cy+ry*math.sin(a)
        d.ellipse((px-5,py-5,px+5,py+5),fill=(245,255,255,180))

        # glow around center
        pulse=math.exp(-((t-1.9)/0.4)**2)
        L=Image.new("L",(W,H),0)
        ImageDraw.Draw(L).ellipse((cx-140,cy-140,cx+140,cy+140),fill=int(90*pulse))
        L=L.filter(ImageFilter.GaussianBlur(75))
        gl=Image.new("RGBA",(W,H),(45,145,255,0)); gl.putalpha(L)
        frame=Image.alpha_composite(frame,gl)

        # logo
        p=max(0,min(1,(t-0.35)/1.2))
        s=0.04+0.96*(1-(1-p)**3)
        size=max(2,int(330*s))
        lg=logo.resize((size,size),Image.Resampling.BILINEAR)
        alpha=int(255*max(0,min(1,t/0.5)))
        if alpha<255:
            lg.putalpha(lg.getchannel("A").point(lambda z:z*alpha//255))
        x=int(cx-lg.width/2); y=int(cy-lg.height/2-12)

        ca=lg.getchannel("A").filter(ImageFilter.GaussianBlur(13))
        gl=Image.new("RGBA",(W,H),(30,135,255,0))
        mask=Image.new("L",(W,H),0); mask.paste(ca,(x,y),ca)
        gl.putalpha(mask.point(lambda z:z//3))
        frame=Image.alpha_composite(frame,gl)
        layer=Image.new("RGBA",(W,H),(0,0,0,0)); layer.alpha_composite(lg,(x,y))
        frame=Image.alpha_composite(frame,layer)

        # wordmark
        q=max(0,min(1,(t-2.8)/0.7))
        if q>0:
            tl=Image.new("RGBA",(W,H),(0,0,0,0)); td=ImageDraw.Draw(tl)
            name="SEAus"
            b=td.textbbox((0,0),name,font=font); tw=b[2]-b[0]
            y0=420 if kind=="console" else 425
            td.text(((W-tw)/2+(1-q)*25,y0),name,font=font,fill=(245,248,252,int(255*q)))
            sub=("SEATTLE  •  AUSTIN" if kind=="console" else "SOFTWARE ENGINEERING STUDIO")
            sb=td.textbbox((0,0),sub,font=small); sw=sb[2]-sb[0]
            td.text(((W-sw)/2,468),sub,font=small,fill=(155,170,190,int(210*q)))
            frame=Image.alpha_composite(frame,tl)

        # ending fade
        if t>dur-0.55:
            q=(dur-t)/0.55
            frame=Image.alpha_composite(frame,Image.new("RGBA",(W,H),(0,0,0,255-int(255*q))))

        frame.convert("RGB").save(os.path.join(root,f"{i:04d}.jpg"),quality=88)

    return root,n

def make_audio(path,dur,variant):
    sr=32000; n=int(sr*dur); t=np.arange(n)/sr; a=np.zeros(n)
    def tone(f,s,l,amp,dec):
        i0=int(s*sr); i1=min(n,int((s+l)*sr))
        if i1<=i0:return
        u=np.arange(i1-i0)/sr
        a[i0:i1]+=amp*np.sin(2*np.pi*f*u)*np.exp(-dec*u)
    if variant==1:
        for z in [(55,0,1.2,.14,2.1),(73.4,.5,1.0,.1,2.8),(146.8,.9,1.4,.08,3.2),
                  (220,1.15,1.2,.1,3.5),(330,1.55,1,.06,4),(440,2,.8,.045,5.2)]:
            tone(*z)
    else:
        for z in [(82.4,.1,1.2,.09,2.6),(123.5,.55,1.1,.06,3.2),(246.9,1.2,1.5,.05,3.8),
                  (369.9,1.65,1.2,.035,4.8),(493.9,2,.9,.03,5.2)]:
            tone(*z)
    fl=min(int(.2*sr),n//2)
    a[:fl]*=np.linspace(0,1,fl); a[-fl:]*=np.linspace(1,0,fl)
    a=a/max(np.max(np.abs(a)),1e-8)*.74
    with wave.open(path,"wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((a*32767).astype(np.int16).tobytes())

def encode(root,n,audio,out):
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",os.path.join(root,"%04d.jpg"),
                    "-i",audio,"-c:v","libx264","-profile:v","main","-level","3.1",
                    "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",
                    "-shortest",out],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

v1root,n1=make_frames("console",6.0)
a1=os.path.join(OUT,"seaus_console_era_sting.wav"); make_audio(a1,6.0,1)
v1=os.path.join(OUT,"Seaus_Console_Era_Ident.mp4"); encode(v1root,n1,a1,v1)

v2root,n2=make_frames("brandid",5.4)
a2=os.path.join(OUT,"seaus_brand_id_sting.wav"); make_audio(a2,5.4,2)
v2=os.path.join(OUT,"Seaus_Classic_Brand_ID_Ident.mp4"); encode(v2root,n2,a2,v2)

print(f"Videos rendered inside: {os.path.abspath(OUT)}")