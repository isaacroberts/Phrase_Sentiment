import numpy as np
import Word

BLANK_CODE=27
BLACK_CODE=13

WB=r'\cb'+str(BLANK_CODE)
BB=r'\cb'+str(BLACK_CODE)
WF=r'\cf'+str(BLANK_CODE)
BF=r'\cf'+str(BLACK_CODE)

class RTF():


    def __init__(self,file):
        self.filename=file
        self.rtf_out=None

    def open(self):
        self.rtf_out=open (self.filename,'w',encoding="utf-8")
        #Header
        self.rtf_out.write(r'{\rtf1\ansi\ansicpg1252\cocoartf1561\cocoasubrtf600')
        self.rtf_out.write(r'{\fonttbl\f0\fswiss\fcharset0 Helvetica;}'+"\n")
        self.rtf_out.write(r'{\colortbl;')
        #Aqua, cyan  #Blue, navy, purple
        self.rtf_out.write(r'\red0\green255\blue128;\red0\green255\blue255;')
        self.rtf_out.write(r'\red0\green128\blue255;\red0\green0\blue255;\red128\green0\blue255;')
        #Pink, salmon, red  #Orange, yellow, lime, Forest
        self.rtf_out.write(r'\red255\green0\blue255;\red255\green0\blue128;\red255\green0\blue0;')
        self.rtf_out.write(r'\red255\green128\blue0;\red255\green255\blue0;\red128\green255\blue0;')
        self.rtf_out.write(r'\red0\green255\blue0;')
        #Vowel colors
        # 0 - 7
        self.rtf_out.write(r'\red0\green0\blue0;\red42\green42\blue42;\red84\green84\blue84;'+
            r'\red126\green126\blue126;\red168\green168\blue168;\red210\green210\blue210;\red255\green255\blue255;')
        # 8 - 12
        self.rtf_out.write(r'\red213\green213\blue213;\red171\green171\blue171;\red129\green129\blue129;'+
            r'\red87\green87\blue87;\red45\green45\blue45;')
        #Dark, Grey, White
        self.rtf_out.write(r'\red50\green50\blue50;\red128\green128\blue128;\red255\green255\blue255;')
        self.rtf_out.write('\n}\n')
        #Margins
        self.rtf_out.write(r'\margl1440\margr1440\vieww10800\viewh8400\viewkind0')
        self.rtf_out.write(r'\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0')
        self.rtf_out.write('\n\n')
        self.rtf_out.write(r'\f0\fs40\cf0\cb0')
        self.rtf_out.write('\n')



    def text(self,line):
        outline=""
        outline+=WB+BF+' '
        for c in line:
            if ord(c) > 128:
                outline+=u"\\u"+str(ord(c))+'.'
            else:
                outline+=c
        self.rtf_out.write(outline+ '\\'+ '\n')


    def write_df(self,df,DICT):

        self.rtf_out.write(WB+BF+' ')


        for index,row in df.iterrows():
            outline=""

            if row['Rd']<=0:
                outline+=WB
            else:
                outline+=r'\cb'+str((6-row['Vw'] -1)%12+1)
            if row['Rd']==row['Sp']:
                outline+=BF
            else:
                outline+=r'\cf'+str(row['Sp'])

            for c in row[0]:
                if ord(c) > 128:
                    outline+=u"\\u"+str(ord(c))+'.'
                else:
                    outline+=c


            if row['IsEnd']==1:
                outline+=WB+'  '

            self.rtf_out.write(outline)

            if row['IsEnd']==2:
                self.divider()

    def write_word(self,word):

        VOWEL_FONTS=True

        n=0
        syl=word.getSyll()
        outline=""
        col=word.getColors()

        col[col>12] +=12
        col[col==Word.NONE]=BLACK_CODE
        lastFont=-1
        for s in range(len(syl)):
            halfIx=max(1,len(syl[s]))

            if col[s][Word.RD]==Word.NONE:
                outline+=WB
            else:
                outline+=r'\cb'+str(col[s][Word.RD])

            if VOWEL_FONTS:
                outline+=r'\cf'+str(col[s][Word.VW])
            else:
                if col[s][Word.SP]==Word.NONE:
                    outline+=BF
                elif col[s][Word.SP]==col[s][Word.RD]:
                    outline+=WF
                else:
                    outline+=r'\cf'+str(col[s][Word.SP])

            #Iterate thru syllable
            for c in range(len(syl[s])):
                if VOWEL_FONTS:
                    if c==halfIx-1:
                        if col[s][Word.SP]!=Word.NONE:
                            outline+=r'\cb'+str(col[s][Word.SP])
                if ord(syl[s][c]) > 128:
                    outline+=u"\\u"+str(ord(syl[s][c]))+'.'
                else:
                    outline+=syl[s][c]
                n+=1
            outline+=WB+WF
            if VOWEL_FONTS:
                if s!=len(syl)-1:
                    outline+='.'
                else:
                    outline+=' '
        outline+=WB+'  '
        self.rtf_out.write(outline)


    def line(self,line,colors=None):
        colors[colors==0]=BLANK_CODE
        outline=""
        prevCat=BLANK_CODE
        for n in range(len(line)):
            if line[n]==' ':
                outline+=WB+' '
                prevCat=BLANK_CODE
            elif colors[n]!=prevCat and line[n]!='-':
                outline+=r'\cb'+str(colors[n])
                prevCat=colors[n]
            if ord(line[n]) > 128:
                outline+=u"\\u"+str(ord(line[n]))+'.'
            else:
                outline+=line[n]
        #outline=outline.lower()
        #outline=outline.replace('-','')
        self.rtf_out.write(outline+ '\\'+ '\n')

    def qline(self,line,colors):
        #Line is quantized into phonemes
        colors[colors==0]=BLANK_CODE
        outline=""
        prevCat=BLANK_CODE
        for n in range(len(line)):
            if line[n]==' ' or line[n]=='':
                outline+=WB+' '
                prevCat=BLANK_CODE
            elif colors[n]!=prevCat and line[n]!='-':
                outline+=r'\cb'+str(colors[n])
                prevCat=colors[n]
            for c in line[n]:
                if ord(c) > 128:
                    outline+=u"\\u"+str(ord(c))+'.'
                else:
                    outline+=c
        #outline=outline.lower()
        #outline=outline.replace('-','')
        self.rtf_out.write(outline+WB+ '\\'+ '\n')

    def dual_color(self,line,font_color,back_color):
        font_color[font_color==0]=BLANK_CODE
        back_color[back_color==0]=BLACK_CODE-12

        prevBC=BLANK_CODE
        prevFC=BLACK_CODE

        outline=""

        for n in range(len(line)):
            if line[n]==' ' or line[n]=='':
                outline+=WB+'  '
                prevBC=BLANK_CODE
            else:
                if font_color[n]!=prevFC and line[n]!='-':
                    outline+=r'\cf'+str(12+font_color[n])
                    prevFC=font_color[n]
                if back_color[n]!=prevBC and line[n]!='-':
                    outline+=r'\cb'+str(back_color[n])
                    prevBC=back_color[n]
                if ord(line[n]) > 128:
                    outline+=u"\\u"+str(ord(line[n]))+'.'
                else:
                    outline+=line[n]
        #outline=outline.lower()
        #outline=outline.replace('-','')
        self.rtf_out.write(outline+WB+BF+ '\\'+ '\n')

    def divider(self,space=3):
        self.rtf_out.write(WB+BF)

        for _ in range(space):
            self.rtf_out.write('\\'+'\n')

        self.rtf_out.write('---------------------------------------')

        for _ in range(space):
            self.rtf_out.write('\\'+'\n')


    def close(self):
        self.rtf_out.write('\n')
        self.rtf_out.write('}')
        self.rtf_out.write('\n')
