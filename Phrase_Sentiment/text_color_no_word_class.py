
import csv
import pandas as pd
import numpy as np
import re
from RTF import RTF
from Word import Word

CAT_AMT=15
BLANK_CODE=15

#Category Header
CAT = "Category"
#IPA, MRC or CMU
DICT = "IPA"

output_file="highlighted_text.rtf"
letters_file="IPA Letters.csv"
combos_file="Combos.csv"
input_file="train.tsv"

letter_df=None
combo_df=None
ipa_dict=None
def main():
    """
Main

    """
    global letter_df
    global combo_df
    global ipa_dict
    print ()

    ipa_dict=read_dict("TWL")
    print (len(ipa_dict),DICT," dictionary entries")

    letter_df,combo_df=read_letters(DICT)
    print (letter_df)

    rtf = RTF("Reviews.rtf")
    rtf.open()


    callback=lambda x: rtf_dual_line(rtf,analyze_line(x),x)
    #callback=lambda x: rtf_line(rtf,color_qmatch(x),x)

    read_tsv("train.tsv",callback)


    rtf.close()

def analyze_line(line):
    print (line)
    ipaline=convert_to_ipa(line)
    c,v=dual_color_match(ipaline)
    #qlet,colors=color_qmatch(ipaline,letter_df,combo_df)
    return ipaline,c,v

def rtf_dual_line(rtf,ipa_c_and_v,line=""):
    ipaline,c,v=ipa_c_and_v
    rtf.dual_color(ipaline,font_color=v,back_color=c)
    rtf.text("")
    rtf.text("")
    rtf.text(line)
    rtf.divider()

def rtf_line(rtf,qline_and_colors=([],[]),line=""):
    qline,colors=qline_and_colors
    if len(qline)>0 and len(colors)>0:
        rtf.qline(qline,colors)
        rtf.text("")
    if line:
        rtf.text("")
        rtf.text(line)
    rtf.divider()

def read_tsv(filename,callback):
    with open ("train.tsv",'r',encoding="utf-8") as text:
        reader=csv.reader(text,delimiter='\t')
        next(reader,None)
        lastSentence=0
        max = 10
        sentence=""
        word_scores={}
        for row in reader:
            sentenceId=int(row[1])
            sentiment=int(row[3])
            if sentenceId > max:
                break
            elif sentenceId>lastSentence:
                #Handle previous
                for word,avg in word_scores.items():
                    word=' '+word+' '
                    score=avg[0]/avg[1]
                    #print (word)
                    #print (avg,sentence, sentence.find(word))
                    #sentence=sentence.replace(word,word+("%.2f " % score))
                callback(sentence)
                #Start new
                lastSentence=sentenceId
                sentence=row[2]
                wordlist=sentence.split(' ')
                for w in wordlist:
                    word_scores[w]=[sentiment,1]
            else:
                wordlist=row[2].split(' ')
                count=len(wordlist)
                #count=1
                for w in wordlist:
                    word_scores[w][0]+=sentiment/count
                    word_scores[w][1]+=1/count


def read_mrc2_dict():
    """
    Read MRC2 dictionary
    Output python dict
    """
    ipa={}
    dict_file="DictMRC/mrc2.dct"
    with open (dict_file,'r',encoding='utf-8') as text:
        for line in text:
            if len(line) > 51:
                #0604200025080150001210000000000000000000000 RO S   ABOARD|@/bOd|@'bOd|02
                line=line[51:]
                entries=line.split("|")
                if entries[2]:
                    #Remove mysterious trailing Q's
                    if entries[2][-2:]==" Q":
                        entries[2]=entries[2][0:-2]
                    word=entries[0].lower()
                    ipa[word]=entries[2]
    return ipa


def read_cmu_dict():

    ipa={}
    dict_file="DictCMU/cmudict.txt"
    with open (dict_file,'r',encoding='utf-8') as text:
        for line in text:
            if line and line[0].isalpha():
                #AARDVARK  AA1 R D V AA2 R K
                entries=line.split("  ")
                word=entries[0].lower()
                deff=entries[1]
                #Remove trailing emphasis digits
                deff= ''.join(c for c in deff if c.isalpha() or c==' ')
                deff=deff.replace(' ','-')
                ipa[word]=deff
    return ipa

def read_ipa_dict():
    ipa={}
    dict_file="Dicts/Full_IPA.txt"
    with open (dict_file,'r',encoding='utf-8') as text:
        for line in text:
            word,defin =line.split('\t')
            if ',' in defin:
                defin=defin.split(',')[0]
            defin=defin.replace('/','')
            defin=defin.replace("ˈ",'')
            ipa[word]=defin
    return ipa

def read_twl_dict():
    ipa={}
    dict_file="Dicts/twl.ipa.tsv"
    with open (dict_file,'r',encoding='utf-8') as text:
        for line in text:
            word,defin =line.split('\t')
            defin=defin.replace('ɜɹ','ɝ')
            ipa[word]=defin
    return ipa

#Read_dict switch function for convienience
def read_dict(format):
    if "MRC" in format:
        return read_mrc2_dict()
    elif "CMU" in format:
        return read_cmu_dict()
    elif format=="IPA":
        return read_ipa_dict()
    elif 'TWL' in format:
        return read_twl_dict()


#Utility function for read_letters
def match_column(c,l):
    maxcol=""
    maxamt=0
    for cc in c.columns:
        for lc in l.columns:
            if cc==lc and cc!=CAT and cc!="English":
                #Find most overlap
                amt=min(c[cc].notnull().sum(),l[lc].notnull().sum())
                if amt>maxamt:
                    maxamt=amt
                    maxcol=cc
    return maxcol

#Read in category breakdown of letters
def read_letters(ipa_fmt="IPA"):

    letters=pd.read_csv(letters_file,encoding='utf-8')
    letters[CAT]=letters[CAT].fillna(BLANK_CODE).astype(int)
    letters['Op']=letters['Op'].fillna('=')
    letters=letters.fillna('_')

    for col in letters.columns:
        if letters[col].dtype=='object':
            letters[col]=letters[col].str.strip()

    #letters[CAT][letters[CAT]>12]+=12
    #letters[CAT][letters['Type']=='V'] +=12

    print ()
    print ("Letters : ")
    print (letters)

    #Combos
    combos=pd.read_csv(combos_file,encoding='utf-8')

    if ipa_fmt not in letters.columns:
        print ("Chosen IPA format ",ipa_fmt," not found")
        return letters,combos



    #If combos is not in correct format
    changes=False
    if ipa_fmt not in combos.columns:
        combos[ipa_fmt]=pd.Series()
        changes=True
    #--Translate any missing values--

    if combos[ipa_fmt].isnull().values.any():
        #Find shared format
        match=match_column(combos,letters)
        #For each empty value
        for ix in combos.index:
            if pd.isna(combos[ipa_fmt][ix]):
                if pd.isna(combos[match][ix]) or combos[match][ix]=="":
                    combos[ipa_fmt][ix]=""
                    combos[match][ix]=""
                else:
                    lets=combos[match][ix].split('-')
                    newlets=[]
                    for l in lets:
                        #Lookup value
                        new='_'
                        for m in range(letters.shape[0]):
                            if letters[match][m]==l:
                                new=letters[ipa_fmt][m]
                                break
                        #print (l,'->',new)
                        newlets.append(new)
                    str='-'.join(l for l in newlets)
                    combos[ipa_fmt][ix]=str
                    changes=True

        #Save updated CSV
        if changes:
            combos.to_csv(combos_file,index=False,encoding='utf-8')
    print ()
    print ("Combos : ")
    print (combos)

    return letters,combos

REMOVE_PUNCTUATION='.,:"[]{}()?\n-'

def direct_translate(word,frm='English',to=DICT):
    result=""
    for index,row in letter_df.iterrows():
        word=word.replace(row[frm],row[to])
    word = '_'+word+"_"
    return word

def q_translate(line,frm='English',to=DICT):
    copy=line.copy()
    for index,row in combo_df.iterrows():
        find=row[frm].replace('-','')
        repl=row[to].replace('-','')
        copy[line==find]=repl
    for index,row in letter_df.iterrows():
        copy[line==row[frm]]=row[to]
    return copy

def convert_to_ipa(line):
    """
    Converts an english string into its IPA translation
    """
    ipa_text=""
    line=line.lower()
    for c in REMOVE_PUNCTUATION:
        line=line.replace(c,' '+c+' ')
#    line="".join(c for c in line if c not in REMOVE_PUNCTUATION)
    for word in line.lower().split(' '):
        if word in ipa_dict:
            ipa_text+=ipa_dict[word]
        elif word:
            if [True for c in word if c.isalpha()]:
                ipa_text+=direct_translate(word)
            else:
                ipa_text+=word
        ipa_text+='  '
    #print (ipa_text)

    for c in REMOVE_PUNCTUATION:
        ipa_text=ipa_text.replace('  '+c+'  ',c)
    return ipa_text

def operation(lval,sign,rval):
    if sign=='=':
        return rval
    if sign=='+':
        return lval+rval
    if sign=='-':
        return lval-rval
    if sign=='*':
        return lval*rval
    if sign=='/':
        return lval/rval
    else:
        return lval

def dual_color_match(line):
    """
    Returns separate vowel color and consonant color
    """
    con=np.full((len(line)),0)
    vow=np.full((len(line)),0)

    lastConStop=0
    setCon=False
    curCon=0
    curVow=6
    lastchar='_'#For two-char sounds
    for i in range(len(line)):
        c=line[i]
        if c==' ' or c in REMOVE_PUNCTUATION:
            curCon=5
            curVow=0
            lastConStop=i+1
        else:
            row=letter_df.loc[letter_df[DICT]==lastchar+c]
            if row.empty:
                row=letter_df.loc[letter_df[DICT]==c]
            else:
                c=lastchar+c
                print (c,"in ",row)
            if not row.empty:
                row=row.iloc[0]
                if row['Type']=='C':
                    #print ("con:",curCon,row['Op'],row['Category'])
                    curCon=operation(curCon,row['Op'],row['Category'])
                    curCon=curCon%12
                    if row['Manner']=='Plosive':
                        #curVow=2
                        lastConStop=i
                    if row['Op']=='=':
                        lastConStop=i
                elif row['Type']=='V':
                    #print ("vow:",curVow,row['Op'],row['Category'])
                    curVow=operation(curVow,row['Op'],row['Category'])
                    curVow=curVow%12
        for m in range(lastConStop,i+1):
            con[m]=curCon
        vow[i]=curVow
    return con,vow

def color_match_with_matchlen(line,letters,combos,vowels=True,consonants=True):
    """
    Shared functionality between color_match and color_qmatch
    Inputs lines and matches letters & combos to colors
    Outputs color array and length of matches
    """
    colors=np.full((len(line)),BLANK_CODE)
    matchlen=np.zeros((len(line),),dtype=np.int)


    for index,row in combos.iterrows():
        search=row[DICT].replace('-','')
        ix=line.find(search)
        while ix!=-1:
            l=len(search)
            if l > matchlen[ix]:
                colors[ix:ix+l] = row[CAT]
                matchlen[ix:ix+l] = l
            ix=line.find(search,ix+1)

    for index,row in letters.iterrows():
        if not vowels and row['Type']=='V':
            continue
        if not consonants and row['Type']=='C':
            continue
        ix=line.find(row[DICT])
        while ix!=-1:
            l=len(row[DICT])
            if l > matchlen[ix]:
                colors[ix:ix+l] = row[CAT]
                matchlen[ix:ix+l] = l
            ix=line.find(row[DICT],ix+1)
    return colors,matchlen

def color_match(line,vowels=True,consonants=True):
    colors,_ = color_match_with_matchlen(line,letter_df,combo_df,vowels,consonants)
    return colors

def color_qmatch(line,vowels=True,consonants=True):
    """
    Inputs a string of words
    Uses combo and letter dictionaries
    Outputs an array of colors by letter
    """
    colors,matchlen=color_match_with_matchlen(line,letter_df,combo_df,vowels,consonants)

    #Clean up quantization by grouping spaces
    prev_space=-1
    for n in range(len(line)-1,0,-1):
        if line[n]==' ' or line[n] in REMOVE_PUNCTUATION:
            if prev_space==-1:
                prev_space=n
        elif prev_space!=-1:
            for m in range(n+1,prev_space):
                matchlen[m]=prev_space-n
            prev_space=-1

    #Count distinct chunks
    #print ('line len=',len(line))
    n=0
    count=1
    #print (line)
    while n<len(matchlen):
        if matchlen[n]>0:
            n+=matchlen[n]
        else:
            n+=1
        count+=1
    #print ('count=',count)
    #Quantize colors and letters
    qcolors=np.zeros((count),dtype=np.int)
    qline=[""]*count
    n=0
    q=0
    while n<len(matchlen) :
        l=matchlen[n]
        if l<=0:
            l=1
        qcolors[q]=colors[n]
        qline[q]=line[n:n+l]
        #print (qline[q])
        n+=l
        q+=1
    qline=np.array(qline)
    #print (qline)
    return qline,qcolors

if __name__=="__main__":
   main()
