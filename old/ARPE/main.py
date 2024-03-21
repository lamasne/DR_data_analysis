# -*- coding: utf-8 -*-

"""
The DR parameters are to be input manually around line 87 
"""



from algorithm.TheQ import Q
filelocation='inputs/'
ListofFiles, WCCFXList, PlotDataList, Q0, DataToSave , Corrupt = Q(filelocation)
#print(Q0)

B=[]
f=[]
X=[]
f1=[]
f2=[]
f3=[]
Q1=[]
Q2=[]
Q3=[]
Ql1=[]
Ql2=[]
Ql3=[]
dR1=[]
dR2=[]
dR3=[]
dX1=[]
dX2=[]
dX3=[]
R1=[]
R2=[]
R3=[]

for i in range(len(ListofFiles)):
    if ListofFiles[i].split('_')[0] == '0' and ListofFiles[i].split('_')[1] == '1':
        f101, Q101 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '0' and ListofFiles[i].split('_')[1] == '2':
        f102, Q102 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '0' and ListofFiles[i].split('_')[1] == '3':
        f103, Q103 = WCCFXList[i][0], Q0[i]
for i in range(len(ListofFiles)):
    if ListofFiles[i].split('_')[0] == '1' and ListofFiles[i].split('_')[1] == '1':
        f201, Q201 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '1' and ListofFiles[i].split('_')[1] == '2':
        f202, Q202 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '1' and ListofFiles[i].split('_')[1] == '3':
        f203, Q203 = WCCFXList[i][0], Q0[i]
for i in range(len(ListofFiles)):
    if ListofFiles[i].split('_')[0] == '2' and ListofFiles[i].split('_')[1] == '1':
        f301, Q301 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '2' and ListofFiles[i].split('_')[1] == '2':
        f302, Q302 = WCCFXList[i][0], Q0[i]
    elif ListofFiles[i].split('_')[0] == '2' and ListofFiles[i].split('_')[1] == '3':
        f303, Q303 = WCCFXList[i][0], Q0[i]      
        
f01=(f101+f201+f301)/3
f02=(f102+f202+f302)/3
f03=(f103+f203+f303)/3

Q01=(Q101+Q201+Q301)/3
Q02=(Q102+Q202+Q302)/3
Q03=(Q103+Q203+Q303)/3

print(f01)
print(f02)
print(f03)

error=0
interval=0
for i in range(len(ListofFiles)):
    if ListofFiles[i].split('_')[1] == '1' and ListofFiles[i].split('_')[0] != '0':
        try:
            
            fi1, Qi1, Qli1 = WCCFXList[i][0], Q0[i], WCCFXList[i][1]
            fi2, Qi2, Qli2 = WCCFXList[i+1][0], Q0[i+1], WCCFXList[i+1][1]
            fi3, Qi3, Qli3 = WCCFXList[i+2][0], Q0[i+2], WCCFXList[i+2][1]
            
            dri1=(1/Qi1-1/Q01)
            dxi1=(-2*(fi1-f01)/f01)
            dri2=(1/Qi2-1/Q02)
            dxi2=(-2*(fi2-f02)/f02)
            dri3=(1/Qi3-1/Q03)
            dxi3=(-2*(fi3-f03)/f03)
            
            ri1=(1/Qi1-3.014e-6)*380/2
            ri2=(1/Qi2-3.66e-6)*248/2
            ri3=(1/Qi3-4.511e-6)*243/2
            
            dRi1=dri1*380/2
            dRi2=dri2*248/2
            dRi3=dri3*243/2
            dXi1=dxi1*380/2
            dXi2=dxi2*248/2
            dXi3=dxi3*243/2
            
            
            
            B.append(float(ListofFiles[i].split('_')[4]))
            Q1.append(Qi1)
            Q2.append(Qi2)
            Q3.append(Qi3)
            Ql1.append(Qli1)
            Ql2.append(Qli2)
            Ql3.append(Qli3)
            f1.append(fi1)
            f2.append(fi2)
            f3.append(fi3)
            dR1.append(dRi1)
            dR2.append(dRi2)
            dR3.append(dRi3)
            dX1.append(dXi1)
            dX2.append(dXi2)
            dX3.append(dXi3)
            R1.append(ri1)
            R2.append(ri2)
            R3.append(ri3)
                
        except:
            error = error + 1
            continue
        
import matplotlib.pyplot as plt
print(str(error)+' errors')

x=B
y=Q1
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$Q1$')
plt.show()

x=B
y=Q2
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$Q2$')
plt.show()

x=B
y=Q3
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$Q3$')
plt.show()

x=B
y=Ql1
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$QL1$')
plt.show()

x=B
y=Ql2
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$QL2$')
plt.show()

x=B
y=Ql3
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$QL3$')
plt.show()



x=B
y=f1
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$f1$')
plt.show()

x=B
y=f2
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$f2$')
plt.show()

x=B
y=f3
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$f3$')
plt.show()


x=B
y=dR1
plt.plot(x,y,'.',label=r'$\Delta R_1$')
y=dR2
plt.plot(x,y,'.',label=r'$\Delta R_2$')
y=dR3
plt.plot(x,y,'.',label=r'$\Delta R_3$')
plt.grid(True)
plt.legend(loc=1, prop={'size': 12})
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$\Delta R$')
plt.show()

x=B
y=dX1
plt.plot(x,y,'.',label=r'$\Delta X_1$')
y=dX2
plt.plot(x,y,'.',label=r'$\Delta X_2$')
y=dX3
plt.plot(x,y,'.',label=r'$\Delta X_3$')
plt.grid(True)
plt.legend(loc=1, prop={'size': 12})
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$\Delta X$')
plt.show()

x=B
y=R1
plt.plot(x,y,'.',label=r'$R_1$')
y=R2
plt.plot(x,y,'.',label=r'$R_2$')
y=R3
plt.plot(x,y,'.',label=r'$R_3$')
plt.grid(True)
plt.legend(loc=1, prop={'size': 12})
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$R$')
plt.show()


aa=[]
bb=[]
a=Q2
for i in range(len(a)): 
    if a[i] < 40000: 
        aa.append(a[i])
        bb.append(B[i])

x=bb
y=aa
plt.plot(x,y,'.')
plt.grid(True)
plt.xlabel(r'B (Oe)')
plt.ylabel(r'$Q2$')
plt.show()




