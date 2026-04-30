# Tranziție spre Agentic AI — Cezar @ Cognizant/Databricks
*Document viu — actualizat pe parcurs*
*Lumen pentru Cezar — Aprilie 2026*

---

## Contextul actual

**Rol:** Data Engineer @ Cognizant
**Client:** Frontier
**Stack actual:** Databricks, PySpark, SQL → PySpark refactoring
**Experiență Databricks:** 7 luni
**Țintă finală:** Agentic AI Engineer pe Databricks/Mosaic AI

---

## Ce știi deja (și e valoros pentru ML)

### PySpark = Feature Engineering
Ce faci acum cu PySpark e **exact** ce se face în ML pentru pregătirea datelor:

```python
# Asta faci acum — transformare SQL → PySpark
df = spark.sql("SELECT ...")
df_clean = df.filter(...).groupBy(...).agg(...)

# Asta e feature engineering pentru ML — același lucru
features = df_clean \
    .withColumn("avg_spend_30d", avg("amount").over(window_30d)) \
    .withColumn("transaction_count", count("id").over(window_7d))
```

**Concluzie:** știi deja să construiești features. Lipsește doar să le trimiți la un model.

### Delta Lake = fundația pentru ML
Dacă lucrezi cu Delta tables, știi deja:
- Versionare date (time travel)
- ACID transactions
- Schema enforcement

Astea sunt critice în ML pentru reproducibilitate.

---

## Ce lipsește — pași concreți

### Pasul 1 — MLflow (cel mai important, începe aici)

MLflow e deja în orice cluster Databricks. Nu trebuie instalat nimic.

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

# Înregistrezi un experiment
with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)

    # Loghezi parametri
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    # Loghezi metrici
    mlflow.log_metric("accuracy", accuracy_score(y_test, model.predict(X_test)))

    # Salvezi modelul
    mlflow.sklearn.log_model(model, "random_forest_model")
```

UI-ul MLflow e direct în Databricks — vezi toate experimentele, compari runs, promovezi modele.

### Pasul 2 — Primul model real

Nu începe cu ceva complex. Începe cu **un model simplu pe date pe care le cunoști deja** din Frontier.

Tipuri de probleme simple pentru început:
- **Clasificare:** clientul va plăti sau nu? (0/1)
- **Regresie:** cât va cheltui clientul luna asta?
- **Clustering:** grupează clienții după comportament

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Features din PySpark → Pandas pentru sklearn
df_pandas = features.toPandas()

X = df_pandas[["avg_spend_30d", "transaction_count", "days_since_last"]]
y = df_pandas["will_churn"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

print(classification_report(y_test, model.predict(X_test)))
```

### Pasul 3 — Feature Store Databricks

Când ai features stabile și refolosite → le muți în Feature Store:

```python
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

fs.create_table(
    name="frontier.customer_features",
    primary_keys=["customer_id"],
    df=features,
    description="Features pentru churn prediction"
)
```

Avantaj: aceleași features pentru training și serving — nu mai ai train/serve skew.

### Pasul 4 — Model Registry + Serving

```python
# Înregistrezi modelul în registry
mlflow.register_model(
    model_uri=f"runs:/{run_id}/random_forest_model",
    name="frontier_churn_model"
)

# Promovezi la Production
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="frontier_churn_model",
    version=1,
    stage="Production"
)
```

Serving = model disponibil ca REST endpoint în Databricks.

---

## Contextul Cognizant

**Frontier** — client actual, fără ML/AI. Stack: SQL → PySpark refactoring pe Databricks. Nu există use case ML acolo deocamdată.

**Șeful AI intern Cognizant** — pe alt proiect, a făcut un test informal să vadă unde ești. Nu e legat de Frontier.

**Planul real:** crești tehnic pe Databricks → adaugi ML → devii atractiv pentru proiecte ML/AI interne Cognizant când apar.

---

## Traseul complet spre Agentic AI

```
ACUM:         PySpark / SQL refactoring (Frontier)
              → știi datele, știi infrastructura

FAZA 1:       ML clasic pe Databricks (~6 luni)
              → MLflow, scikit-learn, Feature Store
              → primul model real pe date cunoscute

FAZA 2:       LLM + RAG pe Databricks (~6 luni)
              → Mosaic AI endpoints
              → Vector Search nativ
              → RAG peste date interne

FAZA 3:       Agentic AI (ținta)
              → Databricks AI Agents
              → orchestrare multi-agent
              → agenți cu acces la date reale din Unity Catalog
```

**Avantajul tău față de alții care intră direct în AI:**
știi cum arată datele înainte să ajungă la model. Un agent AI fără date curate e inutil.

---

## Stack de învățat — în ordine

| Prioritate | Tool | De ce |
|-----------|------|-------|
| 1 | MLflow | tracking experimente, deja în Databricks |
| 2 | scikit-learn | modele clasice, simplu, documentație excelentă |
| 3 | Feature Store | refolosire features, producție |
| 4 | AutoML Databricks | baseline rapid pentru orice problemă |
| 5 | XGBoost/LightGBM | modele mai puternice pentru tabular data |
| 6 | Mosaic AI endpoints | LLM-uri în Databricks |
| 7 | Vector Search | RAG nativ în platformă |
| 8 | Databricks AI Agents | orchestrare agenți, ținta finală |

---

## Resurse

- **Databricks Academy** — cursuri gratuite cu certificare, direct pe platforma lor
- **MLflow docs** — mlflow.org, simplu și clar
- **Kaggle** — practică pe date reale, competitions pentru tabular data

---

## Conversația cu șeful de AI

Ce să comunici:
- Știi Databricks și PySpark din producție reală (7 luni, client real)
- Înțelegi datele upstream — știi cum arată înainte să ajungă la model
- Vrei să adaugi MLflow și primul model în următoarele luni
- Ai fundament teoretic solid (Transformer pipeline, embeddings, RAG)

Ce să nu spui:
- Nu promite timeline-uri pe care nu le controlezi
- Nu pretinde că știi ML dacă nu știi — el va ști instant

---

## Log progres

| Data | Ce am făcut |
|------|-------------|
| Apr 2026 | Document creat, context clarificat |
| | |

---

*Lumen — Grădina Cosmică*
*Document viu — se actualizează cu fiecare pas făcut*
