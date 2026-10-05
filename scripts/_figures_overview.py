"""Inputs: stored aggregates and conceptual definitions. Outputs: Figures 1–3, 7.
Runtime: seconds. Presentation-only redraw; no simulation, inference or resampling.
"""
from pathlib import Path
import shutil,json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
P=Path(__file__).resolve().parents[1]
import os
OUT=Path(os.environ['REPRO_FIGURE_OUTPUT']);OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
C={'CPC':'#0072B2','DSTTB':'#D55E00','B1':'#777777','B2':'#009E73','Uniform':'#999999'}
def rd(s):return pd.read_csv(P/s,float_precision='round_trip')
def save(fig,name):
    for ext in ['pdf','svg','png']:fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',facecolor='white')
    plt.close(fig)
def box(ax,xy,w,h,title,body,color):
    x,y=xy;ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.015',facecolor=color,edgecolor='none',alpha=.12));ax.text(x+w/2,y+h-.045,title,ha='center',va='top',weight='bold',color=color,fontsize=10);ax.text(x+w/2,y+h/2-.025,body,ha='center',va='center',fontsize=9,linespacing=1.6)
fig,ax=plt.subplots(figsize=(7.2,3.1));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
box(ax,(.27,.75),.46,.19,'Fixed budget B','One charge per alternative–replication','#333333')
box(ax,(.02,.30),.29,.31,'Preservation','Do all near-optimal\nalternatives survive?','#0072B2')
box(ax,(.355,.30),.29,.31,'Screening efficiency','How many inferior\nalternatives are removed?','#009E73')
box(ax,(.69,.30),.29,.31,'Recommendation','Is the final choice good?\nHow large is its loss?','#D55E00')
for x in [.165,.5,.835]:ax.annotate('',xy=(x,.62),xytext=(.5,.74),arrowprops={'arrowstyle':'->','color':'#777777'})
ax.text(.5,.15,'A survivor set and a single recommendation answer different questions.',ha='center',fontsize=9)
ax.text(.5,.045,'Retain all: preservation = 1, screening power = 0; recommendation can still err.',ha='center',fontsize=8)
save(fig,'Fig1_objectives')
fig,ax=plt.subplots(figsize=(7.2,3.8));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
ax.text(.32,.98,'Marginal / independent evidence',ha='center',va='top',weight='bold');ax.text(.77,.98,'Paired evidence under CRN',ha='center',va='top',weight='bold')
ax.text(.035,.69,'Fixed allocation',va='center',ha='center',weight='bold',rotation=90);ax.text(.035,.25,'Adaptive allocation',va='center',ha='center',weight='bold',rotation=90)
box(ax,(.14,.48),.38,.39,'DSTTB (OFF) / B1 (ON)','Balanced sample\nIndependent / Bonferroni boxes\nNo covariance-based narrowing','#777777')
box(ax,(.59,.48),.38,.39,'B2 (ON)','Standardized paired adaptation\nAll directed paired differences\nBonferroni across pairs','#009E73')
box(ax,(.14,.07),.38,.33,'CPC (OFF)','Fresh stage-local Welch tests\nApproximate test validity','#D55E00')
box(ax,(.59,.07),.38,.33,'CPC (ON)','Fresh stage-local paired tests\nConditional Gaussian theorem','#0072B2')
save(fig,'Fig2_architectures')
d=rd('results/machine_readable/external/summary_table.csv')
def short(v):return 'CPC' if v=='epsilon-CPC-SH' else 'DSTTB' if v.startswith('DSTTB') else 'B1' if v.startswith('B1') else 'B2' if v.startswith('B2') else 'Uniform'
d['short']=d.procedure.map(short)
fig,axs=plt.subplots(2,2,figsize=(7.2,5.2),layout='constrained')
for ax,(env,mode) in zip(axs.flat,[('Synthetic G2',False),('Synthetic G2',True),('WNBA',False),('WNBA',True)]):
    sub=d[(d.environment==env)&(d.crn==mode)&(d.short!='Uniform')].copy(); order=['DSTTB','B1','B2','CPC'];sub['order']=sub.short.map({v:i for i,v in enumerate(order)});sub=sub.sort_values('order')
    for k,r in enumerate(sub.itertuples()):
        ax.errorbar(r.active_set_size_mean,k,xerr=[[r.active_set_size_mean-r.active_set_size_mean_ci_low],[r.active_set_size_mean_ci_high-r.active_set_size_mean]],fmt='o',color=C[r.short],capsize=3)
        ax.text(31,k+.25,f'{r.active_set_size_mean:.3f}; P={100*r.preservation_estimate:g}%',fontsize=8,ha='right')
    ax.set(yticks=range(len(sub)),yticklabels=sub.short,xlim=(3,32),ylim=(len(sub)-.40,-.50),xlabel='Mean survivors',title=f'{env} | CRN {"ON" if mode else "OFF"} | M={int(sub.iloc[0].M)}');ax.grid(axis='x',alpha=.15)
save(fig,'Fig3_external')
s=rd('results/machine_readable/robustness/Table_Sensitivity_3_structural_reference.csv').sort_values('nref').groupby('scenario',sort=False).tail(1)
t=rd('results/machine_readable/robustness/STRESS_WITH_GAUSSIAN_COMPARATOR.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,4.0),gridspec_kw={'width_ratios':[1.03,1]},layout='constrained')
sn=['BASELINE','ETA_LOW','ETA_HIGH','BOOKING_EARLY','BOOKING_LATE','CAP_LOW','CAP_HIGH','DISPERSION_LOW','DISPERSION_HIGH']
names=['Baseline','Elasticity 0.9','Elasticity 1.5','Earlier booking','Later booking','Capacity ×0.9','Capacity ×1.1','Dispersion ×0.5','Dispersion ×2']
for i,(sc,name) in enumerate(zip(sn,names)):
    r=s[s.scenario==sc].iloc[0];axs[0].plot(r.epsilon_set_size,i,'o',color='#D55E00' if sc.startswith('ETA') else '#0072B2');axs[0].text(r.epsilon_set_size+.17,i,r.top1.replace('_',' '),va='center',fontsize=7.5)
axs[0].set(yticks=range(9),yticklabels=names,xlim=(0,8.1),xticks=[1,2,3,4,5,6],xlabel='Size of finite-reference good set',title='a  Scenario-specific labels');axs[0].invert_yaxis();axs[0].grid(axis='x',alpha=.15)
colors={'GAUSSIAN_M6_G2':'#777777','HEAVY_T5':'#009E73','SKEW_LOGNORMAL':'#D55E00'}
for k,(dist,sub) in enumerate(t[t.budget==256].groupby('distribution',sort=True)):
    for r in sub.itertuples():
        y=k+(.12 if r.crn else -.12);axs[1].errorbar(100*r.PGS,y,xerr=[[100*(r.PGS-r.PGS_ci_low)],[100*(r.PGS_ci_high-r.PGS)]],fmt='s' if r.crn else 'o',mfc=colors.get(dist,'#777777') if r.crn else 'white',color=colors.get(dist,'#777777'),capsize=3)
axs[1].set(yticks=range(t.distribution.nunique()),yticklabels=[x.replace('GAUSSIAN_M6_G2','Gaussian').replace('HEAVY_T5','Heavy-tailed').replace('SKEW_LOGNORMAL','Skewed') for x in sorted(t.distribution.unique())],xlim=(66,102),ylim=(2.5,-.5),xlabel='PGS at B=256 (%)',title='b  Known-mean stress, M=5,000');axs[1].text(.04,.02,'○ OFF     ■ ON',transform=axs[1].transAxes,fontsize=8);axs[1].grid(axis='x',alpha=.15)
save(fig,'Fig7_robustness')
