
import numpy as np

NONE=-1

RD=0
SP=1
VW=2

class Text():
    def __init__(self,t):
        self.ipa=t
        #self.ipa=self.ipa.replace("ˈ","")
        #self.ipa=self.ipa.replace("ˌ","")

    def getSyll(self):
        return np.array([self.ipa])

    def syllAmt(self):
        return 1

    def getColors(self):
        return np.full((1,3),NONE,dtype=int)

    def getVowels(self):
        return np.full((1,1),NONE,dtype=int)

    def color(self,Letters,DICT="IPA"):
        pass



class Word(Text):


    def __init__(self,ipa):
        Text.__init__(self,ipa)
        self.syll=None
        #Beginning and end color

    def getSyll(self):
        if self.syll is None:
            self.syll=self.ipa.split('.')
            self.syll=list(filter(None,self.syll))
        return self.syll

    def syllAmt(self):
        if self.syll is None:
            self.syll=self.ipa.split('.')
            self.syll=list(filter(None,self.syll))
        return len(self.syll)

    def getColors(self):
        if hasattr(self,'colors'):
            return self.colors
        else:
            return None

    def getVowels(self):
        if hasattr(self,'colors'):
            return self.vowels[:][VW]
        else:
            return None

    def color(self,Letters,DICT="IPA"):
        #Calculates but does not return
        if hasattr(self,'colors'):
            return

        print (self.ipa)

        self.getSyll()

        self.colors=np.zeros((len(self.syll),3),dtype=int)
        #lastchar='_'#For two-char sounds

        curCon=0
        backCon=0
        for s in range(len(self.syll)):
            syl=self.syll[s]
            print (syl,'-     ',len(syl),'      -',syl)

            lix=[-1]*len(syl)
            hardness=np.full(len(syl),10)
            mod=[0]*len(syl)
            val=np.zeros(len(syl))
            for i in range(len(syl)):
                c=syl[i]

                """ #Used for two-character symbols
                row=Letters.loc[Letters[DICT]==lastchar+c]
                if not row.empty:
                    lix[i-1]=row.index[0]
                    lix[i]=-1
                else:"""
                row=Letters.loc[Letters[DICT]==c]
                if not row.empty:
                    lix[i]=row.index[0]
                    hardness[i]=row['Hardness']
                    mod[i]=row['Mod'].item()
                    val[i]=row['Category']
                else:
                    print (c, 'not found in letters')


            frontHardMax=0
            backHardMax=0

            frontPole=-1
            frontVal=0

            backPole=-1
            backMod=0
            backVal=0

            frontStrength=0
            midpt=0

            for i in range(len(syl)):
                if hardness[i] > frontHardMax:
                    frontPole=i
                    if val[i]!=0:
                        frontVal = val[i]
                    else:
                        frontVal += mod[i]
                        frontVal %= 12
                    #Reset strength of leading cons
                    frontStrength=hardness[i]

                elif frontStrength > hardness[i]:
                    #If front cons can cover this far
                    if hardness[i] > 5:
                        #If consonant
                        frontVal+=mod[i]
                        frontVal %= 12
                        frontStrength-=1
                    else: #If vowel
                        frontStrength-=(6-hardness[i])

                if frontStrength <0 or i > len(syl)-2:
                    #If out of distance
                    midpt=i
                    break
                """
                else:
                    if hardness[i] >= backHardMax :
                        backPole=i
                        backHardMax =hardness[i]
                        #Set back
                        if val[i]!=0:
                            backVal =val[i]
                        else:
                            backVal += mod[i]
                            backVal %= 12
                        #Add accumulated mod to back
                        backVal+=backMod
                        #Clear acc
                        backMod=0
                        #Mod to 12
                        backVal %= 12

                    elif backPole!=-1:
                        # Shift
                        backVal += mod[i]
                        backVal %= 12

                    elif hardness[i] > 5:
                        #If consonant
                        backMod+=mod[i]
                """
            #if not frontBroken:
            #    for i in range(len(syl),0,-1):


            self.colors[s][RD]=frontVal
            self.colors[s][SP]=backVal


            curVow=-1

            for i in range(len(syl)):
                #TODO : Change this to if vowel:
                if hardness[i] <=5 and hardness[i] >1:
                    #If vowel
                    curVow=val[i]
                    break
            self.colors[s][VW]=curVow
            """


            ### THIS CODE WRITTEN W/ HARDNESS = [min=7, max=1]

            frontPole=-1
            backPole=-1
            min=10
            #print (hardness)
            for i in range(int(len(hardness)/2+1)):
                if hardness[i]<min:
                    min=hardness[i]
                    frontPole=i
            min=10
            for i in range(len(hardness)-1,frontPole,-1):
                if hardness[i]<min:
                    min=hardness[i]
                    backPole=i
            print ('Poles = ',frontPole,syl[frontPole],backPole,syl[backPole])
            print ("  Hard= ",hardness[frontPole],hardness[backPole])

            if s==0:
                curCon=val[frontPole]
            elif hardness[frontPole] < 3:
                curCon=val[frontPole]
            elif hardness[frontPole] < 5:
                curCon+=mod[frontPole]
                curCon %= 12

            print ('*0  ',curCon)

            midpt=backPole
            if hardness[backPole] < 4:
                dip=hardness[backPole]
                for i in range(backPole-1,frontPole,-1):
                    print (dip,hardness[i])
                    if hardness[i] > dip:
                        dip= hardness[i]
                    elif hardness[i] < dip:
                        #print ("dip out @",i,syl[i],syl,hardness[i],dip)
                        break
                    midpt=i
            else:
                midpt=backPole+1
            print (syl,'midpt=',midpt)

            for i in range(frontPole+1,midpt,1):
                print ("*    f-m",curCon,mod[i],syl[i])
                curCon+=mod[i]
                curCon %= 12
            print ('*2  ',curCon)
            #hardDiff=hardness[backPole] - hardness[frontPole]
            #print ('  hard diff=',hardDiff)

            if hardness[backPole] <=2:
                backCon=val[backPole]
            elif hardness[backPole] <4 :
                print ('^   f->b+',curCon)
                backCon=curCon
                backCon+=mod[backPole]
                backCon %= 12
            else:#if hardDiff < 5:
                backCon=curCon
                print ("^   f->b.")

            print ('^0  ',backCon)

            if hardness[backPole] <4:
                for i in range(backPole-1,midpt-1,-1):
                    backCon+=mod[i]
                    backCon %= 12
                    print ("^    b-m",backCon,mod[i],syl[i])
                print ('^1  ',backCon)
                for i in range(backPole+1,len(syl)):
                    backCon+=mod[i]
                    backCon %= 12
                    print ("^    b-l",backCon,mod[i],syl[i])
                print ('^2  ',backCon)

            #Leading characters work differently
            for i in range(frontPole-1,-1,-1):
                if syl[i]=='s':
                    pass
                elif syl[i]=='ˌ':
                    #Pause
                    backCon += 1
                    backCon %= 12
                elif syl[i]=='ˈ':
                    #Emphasis
                    backCon -= 1
                    backCon %= 12
                else:
                    print ("Unseen Leading Character:",syl[i],'in',syl)


            print ('*3  ',curCon)
            print ('^3  ',backCon)
            self.colors[s][RD]=curCon
            self.colors[s][1]=backCon
            """
        # / for syllable

#Util function
def operation(lval,sign,rval):
    if sign=='=':
        return rval
    if sign=='+':
        return (lval+rval)%12
    if sign=='-':
        return (lval-rval)%12
    if sign=='*':
        return lval*rval
    if sign=='/':
        return lval/rval
    if sign=='#':
        if lval==0:
            return rval
        else :
            return lval
    else:
        return lval
