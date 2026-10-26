from build_powerbi import *
from build_powerbi import PROJECT_ROOT
import sys, ast, numpy as np
from sklearn.model_selection import train_test_split
from scipy.stats import ks_2samp, chi2_contingency

def churn():
 repo='-E-commerce-Churn-Model-S03-26-Equipo-40-Data-Science';r=Report(repo,'Churn Intelligence','DEMOSTRACIÓN SINTÉTICA del Streamlit original · 800 clientes · no son predicciones de producción')
 code=(PROJECT_ROOT/'Dashboard/webapp/data_loader.py').read_text();node=next(n for n in ast.parse(code).body if isinstance(n,ast.FunctionDef) and n.name=='_generate_demo_data');ns={'np':np,'pd':pd};exec(compile(ast.Module(body=[node],type_ignores=[]),'demo','exec'),ns);dist,glob,d,vips=ns['_generate_demo_data']()
 r.table('Clientes',d,metrics('Clientes',[('Clientes','COUNTROWS(Clientes)'),('Riesgo','AVERAGE(Clientes[churn_probability])'),('Valor','SUM(Clientes[monetary])'),('LTV','SUM(Clientes[lifetime_value])'),('Frecuencia','AVERAGE(Clientes[frequency])'),('Recencia','AVERAGE(Clientes[recency])')]))
 p90=vips.churn_probability.quantile(.9);p70=vips.churn_probability.quantile(.7);vips['Estrategia']=np.where(vips.churn_probability>=p90,'Llamada Ejecutiva',np.where(vips.churn_probability>=p70,'Email + Descuento','Seguimiento CSM'));vips['Urgencia']=np.where(vips.churn_probability>=p90,'Alta',np.where(vips.churn_probability>=p70,'Media','Baja'));vips['RetornoHipotetico']=vips.lifetime_value*.18;vips['InversionHipotetica']=vips.lifetime_value*.05
 r.table('Plan',vips,metrics('Plan',[('VIP','COUNTROWS(Plan)'),('Inversion','SUM(Plan[InversionHipotetica])'),('Retorno','SUM(Plan[RetornoHipotetico])')]))
 filters=[('Clientes','customer_level'),('Clientes','risk_segment')]
 for pg,label,c1,m1,c2,m2 in [('resumen','01 · Resumen ejecutivo','customer_level','KPI_Clientes','risk_segment','KPI_Valor'),('predicciones','02 · Riesgo ML · demo','risk_segment','KPI_Riesgo','customer_level','KPI_Riesgo'),('valor','03 · Valor y riesgo','risk_segment','KPI_LTV','customer_level','KPI_Valor'),('rfm','04 · Segmentación RFM','rfm_score','KPI_Frecuencia','customer_level','KPI_Recencia')]:
  r.page(pg,label,filters);r.cards('Clientes',['KPI_Clientes','KPI_Riesgo','KPI_Valor','KPI_LTV']);r.chart('Clientes',c1,m1,c1,30,270);r.chart('Clientes',c2,m2,c2,650,270);r.tablevisual('Clientes',['customer_level','risk_segment','KPI_Clientes','KPI_Riesgo','KPI_Frecuencia','KPI_Recencia','KPI_LTV'],'Segmentos · resultados sintéticos del modo demo original',30,570,1220,260)
 r.page('plan','05 · Plan de acción VIP',[('Plan','Estrategia'),('Plan','Urgencia')],note='DEMO · supuestos del original: inversión 5% del LTV y retorno 18%. No son ROI medido ni recomendaciones validadas.')
 r.cards('Plan',list(r.measures['Plan']));r.chart('Plan','Estrategia','KPI_VIP','Intervenciones propuestas',30,270);r.chart('Plan','Urgencia','KPI_Inversion','Presupuesto hipotético',650,270);r.tablevisual('Plan',['customer_id','Estrategia','Urgencia','lifetime_value','churn_probability','RetornoHipotetico','InversionHipotetica'],'Matriz de intervención',30,570,1220,260)
 return r.finish('Cinco páginas equivalentes a las cinco secciones de Streamlit. Los CSV proceden exclusivamente de `_generate_demo_data()` del proyecto, semilla 42. La tasa global y los agregados se calculan de la misma tabla de 800 clientes; se omiten los KPIs globales estáticos del demo que no coinciden con sus filas. Supabase no está conectado. Para producción exporta las vistas sin renormalizar importes ni generar valores ficticios.')
if __name__=='__main__':
    print(churn())
