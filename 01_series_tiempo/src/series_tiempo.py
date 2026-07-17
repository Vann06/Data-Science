from pathlib import Path
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress, fligner
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing

plt.rcParams['figure.figsize']=(11,4.5)
plt.rcParams['axes.grid']=True

paths=[Path('../data/raw/guatemala_temperatura.csv'),Path('01_series_tiempo/data/raw/guatemala_temperatura.csv')]
path=next((p for p in paths if p.exists()),None)
if path is None: raise FileNotFoundError('No se encontró guatemala_temperatura.csv')
df=pd.read_csv(path,parse_dates=['month']).sort_values('month')
ts=df.set_index('month').asfreq('MS')
print('Datos:',df.shape,'Rango:',df.month.min().date(),'a',df.month.max().date())
print('Faltantes:',int(df.isna().sum().sum()),'Duplicados:',int(df.month.duplicated().sum()))

print('\nEJERCICIO 1: EXTREMOS Y TENDENCIA')
cols=[c for c in df.columns if c.endswith('_c')]
rows=[]; x=np.arange(len(df))
for c in cols:
    imin,imax=df[c].idxmin(),df[c].idxmax(); reg=linregress(x,df[c])
    rows.append({'variable':c,'min':df.loc[imin,c],'fecha_min':df.loc[imin,'month'].date(),'max':df.loc[imax,c],'fecha_max':df.loc[imax,'month'].date(),'media':df[c].mean(),'pendiente_C_decada':reg.slope*120,'p_tendencia':reg.pvalue})
summary=pd.DataFrame(rows).set_index('variable')
print(summary.round(4))
ts[cols].rolling(12,center=True).mean().plot(title='Media móvil de 12 meses'); plt.ylabel('°C'); plt.show()

print('\nEJERCICIOS 2 Y 3: TRAIN/TEST Y ESTACIONARIEDAD')
series=ts['temperature_2m_c'].rename('temperatura_2m_c')
train,test=series.iloc[:-36],series.iloc[-36:]
print('Train:',train.index.min().date(),'a',train.index.max().date(),len(train))
print('Test:',test.index.min().date(),'a',test.index.max().date(),len(test))
ax=train.plot(label='train'); test.plot(ax=ax,label='test'); ax.legend(); plt.show()
seasonal_decompose(train,model='additive',period=12,extrapolate_trend='freq').plot(); plt.show()

def tests(s):
    s=s.dropna(); a=adfuller(s,autolag='AIC'); k=kpss(s,regression='c',nlags='auto')
    return {'ADF_p':a[1],'KPSS_p':k[1]}
print('Original:',tests(train))
print('Diferencia estacional 12:',tests(train.diff(12)))
blocks=np.array_split(train.to_numpy(),4)
print('Fligner p para varianza:',fligner(*blocks).pvalue)

print('\nEJERCICIO 4: ACF/PACF Y MODELOS')
d12=train.diff(12).dropna(); plot_acf(d12,lags=36); plt.show(); plot_pacf(d12,lags=36,method='ywm'); plt.show()
specs={
'SARIMA(1,0,1)(0,1,1,12)':((1,0,1),(0,1,1,12)),
'SARIMA(1,0,2)(0,1,1,12)':((1,0,2),(0,1,1,12)),
'SARIMA(2,0,1)(0,1,1,12)':((2,0,1),(0,1,1,12))}
fits={n:SARIMAX(train,order=o,seasonal_order=s,trend='c',enforce_stationarity=False,enforce_invertibility=False).fit(disp=False,maxiter=300) for n,(o,s) in specs.items()}

print('\nEJERCICIO 5: VALIDACIÓN')
rows=[]
for n,r in fits.items():
    burn=max(r.loglikelihood_burn,24); resid=pd.Series(r.resid).iloc[burn:].dropna()
    lb=acorr_ljungbox(resid,lags=[12,24],model_df=max(len(r.params)-1,0),return_df=True)
    rows.append({'modelo':n,'AIC':r.aic,'BIC':r.bic,'LB_p12':lb.loc[12,'lb_pvalue'],'LB_p24':lb.loc[24,'lb_pvalue']})
comparison=pd.DataFrame(rows).sort_values('AIC'); print(comparison.round(4))
best_name='SARIMA(1,0,1)(0,1,1,12)'; best=fits[best_name]
print('\nCoeficientes del mejor modelo:'); print(pd.DataFrame({'coef':best.params,'p':best.pvalues}).round(5))

print('\nEJERCICIO 6: PRONÓSTICO')
def metrics(y,p):
    y=np.asarray(y); p=np.asarray(p)
    return {'MAE':mean_absolute_error(y,p),'RMSE':mean_squared_error(y,p)**0.5,'MAPE_%':np.mean(np.abs((y-p)/y))*100}
fc=best.get_forecast(len(test)); pred=fc.predicted_mean; pred.index=test.index; ci=fc.conf_int(); ci.index=test.index
print(best_name,metrics(test,pred))
ax=train.iloc[-120:].plot(label='train'); test.plot(ax=ax,label='real'); pred.plot(ax=ax,label='SARIMA'); ax.fill_between(test.index,ci.iloc[:,0],ci.iloc[:,1],alpha=.2); ax.legend(); plt.show()

print('\nEJERCICIO 7: OTROS MODELOS')
hw=ExponentialSmoothing(train,trend='add',seasonal='add',seasonal_periods=12,initialization_method='estimated').fit(); p_hw=hw.forecast(len(test)); p_hw.index=test.index
ses=SimpleExpSmoothing(train,initialization_method='estimated').fit(); p_ses=ses.forecast(len(test)); p_ses.index=test.index
p_naive=pd.Series(np.resize(train.iloc[-12:].to_numpy(),len(test)),index=test.index)
preds={best_name:pred,'Holt-Winters':p_hw,'Suavizamiento simple':p_ses,'Naive estacional':p_naive}
result=pd.DataFrame([{'modelo':n,**metrics(test,p)} for n,p in preds.items()]).sort_values('RMSE'); print(result.round(4))

print('\nEJERCICIO 8: CONCLUSIÓN')
coverage=((test>=ci.iloc[:,0])&(test<=ci.iloc[:,1])).mean()*100
print('Cobertura intervalo 95%:',round(coverage,2),'%')
print('El modelo es útil para promedios mensuales si RMSE<1 °C y MAPE<5%; no predice valores diarios ni extremos.')
order,seasonal=specs[best_name]
final=SARIMAX(series,order=order,seasonal_order=seasonal,trend='c',enforce_stationarity=False,enforce_invertibility=False).fit(disp=False,maxiter=300)
f=final.get_forecast(12)
future=pd.DataFrame({'pronostico_C':f.predicted_mean,'inferior_95':f.conf_int().iloc[:,0],'superior_95':f.conf_int().iloc[:,1]})
print('\nPronóstico 12 meses posteriores:'); print(future.round(3))
