# Reporte breve: LSTM con características Catch22

## Objetivo

El ejercicio evaluó si las 22 características de Catch22 pueden complementar una red LSTM para pronosticar la serie `total_internacional`. El resultado se comparó con el mejor LSTM obtenido para esa misma serie: el Modelo 1 del notebook 2 y con una ablación global que no utiliza Catch22.

## Metodología

Se utilizaron las siete series mensuales generadas en el notebook 3, cada una con 210 observaciones entre enero de 2009 y junio de 2026. La división fue cronológica: 147 meses para entrenamiento y 63 para prueba.

La LSTM enriquecida recibió una ventana de 12 meses y las 22 características Catch22 estandarizadas correspondientes a cada serie. El entrenamiento se realizó de manera global con las siete series, produciendo 945 ventanas de entrenamiento. Para medir el aporte del perfil Catch22 también se ajustó una LSTM global con la misma información temporal, pero sin las 22 características.

### Elección del modelo de referencia

El modelo de referencia es el Modelo 1 del notebook 2 porque fue el mejor LSTM obtenido para `total_internacional`, que es también la serie pronosticada por el modelo con Catch22. Los resultados geográficos del notebook 1 no se usan como referencia directa: América del Centro y Europa tienen escalas diferentes, por lo que sus errores absolutos no pueden compararse directamente con los de la serie total. En términos relativos, América del Centro obtuvo nRMSE de 54.11%, la serie total aproximadamente 59.03% y Europa 79.88%; aun así, para el inciso 2.14 corresponde comparar modelos de la misma serie.

El pronóstico de los 63 meses de prueba fue recursivo: cada valor pronosticado se utilizó como entrada del paso siguiente, sin incorporar observaciones reales futuras como rezagos.

## Resultados

| Modelo | Series de ajuste | Entradas | MAE | RMSE | MAPE |
|---|---:|---|---:|---:|---:|
| LSTM global con Catch22 | 7 | 12 rezagos + 22 Catch22 | 79,015 | 89,244 | 56.65% |
| LSTM base de la serie total (Modelo 1) | 1 | 12 rezagos | 111,556 | 126,236 | 47.48% |
| LSTM global sin Catch22 | 7 | 12 rezagos | 214,230 | 268,278 | 90.73% |

### Comparación con el LSTM base de la serie total

| Indicador | Cambio del modelo Catch22 |
|---|---:|
| MAE | Reducción de 29.2% |
| RMSE | Reducción de 29.3% |
| MAPE | Aumento relativo de 19.3% |

La LSTM con Catch22 comete errores absolutos menores, reflejados en MAE y RMSE. Sin embargo, su MAPE es mayor. Esto significa que el modelo se aproxima mejor en términos de cantidad de visitantes, especialmente en meses de mayor volumen, pero presenta errores relativos más grandes en observaciones con niveles menores.

Este comportamiento no es contradictorio. MAE y RMSE miden el error en las unidades originales y dan mayor peso a desviaciones grandes; MAPE divide cada error por el valor observado y penaliza con fuerza los errores cometidos cuando el total real es relativamente bajo. La recuperación posterior a la pandemia contiene precisamente cambios de nivel que pueden producir esta diferencia entre métricas.

## Aporte observado de Catch22

La ablación global sin Catch22 obtuvo un RMSE de 268,278 y generó un pronóstico recursivo inestable. Al incorporar Catch22, el RMSE de este diseño global disminuyó 66.7%. El perfil ayuda a distinguir las siete series después de que sus valores temporales se escalan individualmente, proporcionando información sobre periodicidad, autocorrelación, distribución y complejidad.

No existía una obligación teórica de que el modelo mejorara. Catch22 resume propiedades estructurales, pero no proporciona directamente los valores futuros. Podía mejorar si facilitaba la transferencia de patrones entre series, no cambiar de forma importante o empeorar por el aumento de dimensionalidad y la corta longitud de las series. Los resultados obtenidos son plausibles, aunque no demuestran una superioridad general porque una de las tres métricas empeoró.

## Limitaciones

1. Los perfiles Catch22 disponibles fueron calculados sobre los 210 meses completos. Aunque las observaciones reales de prueba no se usaron como rezagos ni para ajustar los pesos, el perfil estructural resume también el horizonte de prueba. Por ello el experimento es transductivo y sus resultados pueden ser optimistas.
2. La comparación con el notebook 2 modifica dos elementos al mismo tiempo: incorpora Catch22 y utiliza entrenamiento global con siete series. La ablación ayuda a separar los efectos, pero no elimina completamente esta diferencia experimental.
3. El horizonte de 63 meses es extenso para un pronóstico recursivo. Los errores se acumulan y la predicción tiende a estabilizarse, suavizando picos y cambios de nivel.
4. El quiebre causado por la pandemia y la recuperación posterior hacen que el conjunto de prueba tenga una dinámica distinta a buena parte del entrenamiento.

## Conclusiones

- Catch22 redujo de forma importante MAE y RMSE frente al mejor LSTM obtenido para la misma serie total, pero empeoró MAPE. El resultado es mixto y debe juzgarse según la métrica más relevante para el objetivo.
- La ablación indica que las características Catch22 aportan una firma útil para distinguir series heterogéneas dentro de un modelo global.


