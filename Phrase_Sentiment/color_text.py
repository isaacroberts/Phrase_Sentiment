import sys
import argparse
import csv
import re

import pandas as pd
import numpy as np

from RTF import RTF
import Word as Word__
from Word import Word, Text

#TWL, IPA, MRC or CMU
DICT = "TWL"
#Category Header
CAT = "Category"
ENG='English'

output_file="highlighted_text.rtf"
letters_file="Dict/IPA Letters.csv"
suffix_file="Dict/Suffixes.csv"
input_file="Data/train.tsv"

letter_df=None
ipa_dict=None
suffix_df=None

word_df=None
syll_df=None

def main(max=-1):
    """
Main

    """
    rtf = RTF("Reviews.rtf")
    rtf.open()

    lets, sylls=get_sylls(max)

    sys.stdout=sys.__stdout__

    lets.to_csv("letters.csv",index=False,encoding='utf-8')
    rtf.write_df(sylls,DICT)
    rtf.close()


def get_sylls(max=-1):
    global letter_df
    global ipa_dict
    global suffix_df
    global word_df
    global syll_df

    print ()

    ipa_dict=read_dict(DICT)
    print (len(ipa_dict),DICT," dictionary entries")

    sys.stdout=open('dict.txt','w')
    for k,v in ipa_dict.items():
        k=str(k)
        v=v.ipa

        k=k.replace('e','E')
        v=v.replace('eɪ','A')
        print (k,'\t',v)


    sys.stdout=sys.__stdout__

    letter_df=read_letters(DICT)
    print (letter_df)

    suffix_df=read_suffixes()

    #word_cols=["English",DICT,'SylIx','SylAmt']
    #word_df=pd.DataFrame(columns=word_cols)

    syll_cols=[DICT,"Score","Len","Rd","Sp","Vw","Ob","IsEnd"]
    syll_df=pd.DataFrame(columns=syll_cols)

    sys.stdout=open('log.txt','w')
    #sys.stdout=None

    callback=lambda x,y: analyze_line(x,y)
    read_tsv("train.tsv",callback,max)

    print (syll_df)

    return letter_df,syll_df






def analyze_line(line,scores=None):
    global syll_df

    ipaline=convert_to_ipa(line)

    if len(ipaline)==0:
        return

    total_syl=0
    for eng,word in ipaline:
        word.color(letter_df,DICT)
        total_syl+=word.syllAmt()
        print (total_syl)

    append=pd.DataFrame(columns=syll_df.columns,index=range(total_syl))

    wordIx=syll_df.columns.get_loc(DICT)
    scoreIx=syll_df.columns.get_loc('Score')
    lenIx=syll_df.columns.get_loc('Len')
    rdIx=syll_df.columns.get_loc('Rd')
    spIx=syll_df.columns.get_loc('Sp')
    vwIx=syll_df.columns.get_loc('Vw')
    obIx=syll_df.columns.get_loc('Ob')
    endIx=syll_df.columns.get_loc('IsEnd')

    append.iloc[:,endIx]=0
    if scores is None:
        append.iloc[:,scoreIx]=-1
    append.iloc[:,obIx]=0


    ix=0
    for eng,word in ipaline:
        l=word.syllAmt()
        append.iloc[ix:ix+l,wordIx]=word.getSyll()

        if scores is not None:
            score=scores[eng][0]/scores[eng][1]
            append.iloc[ix:ix+l,scoreIx]=score

        append.iloc[ix:ix+l,lenIx]=l

        append.iloc[ix:ix+l,rdIx]=word.getColors()[:,Word__.RD]
        append.iloc[ix:ix+l,spIx]=word.getColors()[:,Word__.SP]
        append.iloc[ix:ix+l,vwIx]=word.getColors()[:,Word__.VW]
        append.iloc[ix+l-1 ,endIx]=1
        ix +=l
    append.iloc[ix-1,endIx]=2

    syll_df=syll_df.append(append,ignore_index=True)

def rtf_words(rtf,wordline,english):

    for word in wordline:
        rtf.write_word(word)
    rtf.text("")
    rtf.text("")
    rtf.text(english)
    rtf.divider()


def read_tsv(filename,callback,amt=-1):

    with open ("Data/train.tsv",'r',encoding="utf-8") as text:
        reader=csv.reader(text,delimiter='\t')
        next(reader,None)
        lastSentence=0
        counter=0

        sentence=""
        word_scores={}
        for row in reader:
            sentenceId=int(row[1])
            sentiment=int(row[3])
            text=sanitize_line(row[2])

            if amt!=-1 and counter > amt:
                break
            elif sentenceId>lastSentence:
                #Handle previous
                counter+=1
                for word,avg in word_scores.items():
                    score=avg[0]/avg[1]

                #Callback
                callback(sentence,word_scores)
                #Start new
                lastSentence=sentenceId
                sentence=text
                #sentence=sentence.replace("does n't","doesn't")
                wordlist=text.lower().split(' ')
                for w in wordlist:
                    word_scores[w]=[sentiment,1./len(wordlist)]
            else:
                wordlist=text.lower().split(' ')
                count=len(wordlist)
                #count=1
                for w in wordlist:
                    if w in word_scores:
                        word_scores[w][0]+=sentiment/count
                        word_scores[w][1]+=1./count
                    else:
                        print (w ,'not found in word_scores')

def read_twl_dict():
    ipa={}
    dict_file="Dict/twl.ipa.tsv"

    dict=pd.read_csv(dict_file,'r',encoding='utf-8',delimiter='\t',names=['Word','Def'])


    dict['Word']=dict['Word'].str.lower()
    #Fixes two-char problem
    dict['Def']=dict['Def'].str.replace('ɜɹ','ɝ')
    dict['Def']=dict['Def'].str.replace('əɹ','ɚ')


    for row in dict.itertuples():
        if row[1] not in ipa:
            ipa[row[1]]=Word(row[2])
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

BLANK_CODE=15
#Read in category breakdown of letters
def read_letters(ipa_fmt="IPA"):

    letters=pd.read_csv(letters_file,encoding='utf-8')

    #letters.drop(columns='Shade',inplace=True)
    letters.dropna(axis=0,how='all',inplace=True)

    letters[CAT]=letters[CAT].fillna(BLANK_CODE).astype(int)
    letters['Mod']=letters['Mod'].str.strip()
    letters['Mod'].replace('+','',inplace=True)
    letters['Mod'].replace('',np.nan,inplace=True)
    letters['Mod'].fillna(0,inplace=True)
    letters['Mod']=letters['Mod'].astype(int)

    letters.fillna('_',inplace=True)

    for col in letters.columns:
        if letters[col].dtype=='object':
            letters[col]=letters[col].str.strip()
    print ()
    print ("Letters : ")
    print (letters)

    return letters

def read_suffixes():
    suff=pd.read_csv(suffix_file,encoding='utf-8')
    suff = suff.apply(lambda x: x.str.strip()).replace('', np.nan)
    suff.dropna(axis=(0,1),how='all',inplace=True)
    suff.fillna('_',inplace=True)
    print ("Suffixes")
    print (suff)
    return suff


def convert_to_ipa(line):
    """
    Converts an english string into its IPA translation
    """

    line=sanitize_line(line)
    splitline=line.split(' ')
    words=[]
    for word in splitline:
        word=word.strip()
        #word=word.replace(' ','')
        #word=word.replace('\t','')
        if len(word)==0:
            continue
        if word in ipa_dict:
            words.append((word,ipa_dict[word]))
        elif word in REMOVE_PUNCTUATION or word=='.':
            words.append((word,Text(word)))
            pass
        elif word:
            #Try removing suffixes
            w=try_suffixes(word)
            if w is not None:
                print ("Found suffix for ",word,w.ipa)
                ipa_dict[word] = w
                words.append((word,w))
            else:
                ipa=direct_translate(word,frm=ENG,to=DICT)
                if len(ipa)>0:
                    print("Adding madeup IPA. ",word,'=',ipa)
                    w=Word(ipa )
                    ipa_dict[word]=w
                    words.append((word,w))
    return words

def try_suffixes(word):
    """
    Uses Suffix_df

    Trys removing suffixes from word
        and checking if its in the dictionary without it.
    Then adds the suffixes' IPA to the IPA found in the dictionary.

    Returns the new Word if found. Does not add it to dictionary.
    """
    for ix,suff in suffix_df.iterrows():
        if word.endswith(suff[ENG]):
            if word==suff[ENG]:
                found=True
                #TODO
                #Add suffix to previous word
                return None
            else:
                #Remove suffix
                clippedEng=word[0:-len(suff[ENG])]
                assert (len(clippedEng) > 0)
                #Look for suffixless version
                if clippedEng in ipa_dict:
                    #Find suffixless translation
                    ipa=ipa_dict[clippedEng].ipa
                    #Add IPA of suffix
                    ipa+=suff[DICT]
                    #Make a new Word
                    return Word(ipa)
                else:
                    if suff['Eats'] != "_":
                        #If the suffix eats a letter
                        clippedEng+=suff['Eats']
                        if clippedEng in ipa_dict:
                            #Find suffixless translation
                            ipa=ipa_dict[clippedEng].ipa
                            #Add IPA of suffix
                            ipa+=suff[DICT]
                            #Make a new Word
                            return Word(ipa)
    return None

def direct_translate(word,frm=ENG,to=DICT):
    result=""
    for index,row in letter_df.iterrows():
        word=word.replace(row[frm],row[to])

    #Rough fixes
    lastchar='_'
    mod=1
    for c in word:
        #Prevent multiples
        if c!=lastchar:
            lastchar=c
            result+=c
            #Add arbitrary syllables
            if mod==3:
                result+='.'
                mod=0
            mod+=1

    #result = '|'+result+"|"
    return result

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

def read_ipa_dict():
    ipa={}
    dict_file="Dict/Full_IPA.txt"
    with open (dict_file,'r',encoding='utf-8') as text:
        for line in text:
            line=line.replace('\n','')
            word,defin =line.split('\t')
            if ',' in defin:
                defin=defin.split(',')[0]
            defin=defin.replace('/','')
            defin=defin.replace("ˈ",'')

            ipa[word]=Word(defin)
    return ipa


def read_mrc2_dict():
    """
    Read MRC2 dictionary
    Output python dict
    """
    ipa={}
    dict_file="Dict/DictMRC/mrc2.dct"
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
                    ipa[word]=Word(entries[2])
    return ipa


def read_cmu_dict():

    ipa={}
    dict_file="Dict/DictCMU/cmudict.txt"
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
                ipa[word]=Word(deff)
    return ipa


REMOVE_PUNCTUATION=',:"[]{}()?!\n-'
def sanitize_line(line):
    line=line.lower()
    for c in REMOVE_PUNCTUATION:
        line=line.replace(c,' '+c+' ')
    line=line.replace('  ',' ')
    return line

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("max", type=int,default=-1,help="Amount of words to analyze.",nargs="?")

    args=parser.parse_args()

    main(args.max)
