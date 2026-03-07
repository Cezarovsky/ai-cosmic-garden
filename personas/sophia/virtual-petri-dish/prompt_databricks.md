# Prompt pentru Notebook Databricks Profesional

## Structure Guidelines

### Cell Organization
1. **Cell Types**: Markdown pentru secțiuni, Python pentru cod
2. **No try-catch blocks** - lasă erorile să apară natural
3. **No print statements** - folosește expresii directe pentru output
4. **Cell separation** - o operație logică per celulă
5. **Clean outputs** - expresii care se afișează automat

### Code Style Examples

```python
# ✅ Good - expresie directă afișează rezultatul
table_count = spark.table("table_name").count()
f"Records loaded: {table_count:,}"

# ✅ Good - afișare automată DataFrame
df.show(10, truncate=False)

# ✅ Good - inspecție schema
df.printSchema()

# ❌ Bad - nu folosi
try:
    df = spark.table("table")
    print(f"Success: {df.count()}")
except Exception as e:
    print(f"Error: {e}")
```

## Error Handling Philosophy

### Let Errors Fail Fast
- **Nu ascunde erorile** - nu le prinzi și nu le masci
- **Fail fast principle** - lasă scriptul să cadă dacă e ceva în neregulă
- **Transparent debugging** - erorile trebuie să fie vizibile

### Conditional Logic for Optional Operations
```python
# Verifică dacă tabela există înainte
tables = spark.catalog.listTables("schema_name")
table_exists = any(t.name == "target_table" for t in tables)

if table_exists:
    df = spark.table("schema.target_table")
    df.count()
else:
    "Table not found - expected for initial analysis"
```

## Professional Notebook Format

### Structure Template
```markdown
# Title - Business Problem Analysis
## Subtitle - Technical Investigation

**JIRA Ticket:** DP-XXXX
**Test Case:** DP-RXXX  
**Issue:** Clear problem statement
**Environment:** SIT/UAT/PROD

### Problem Summary
**⚠️ FUNDAMENTAL ISSUE:** Core problem description
Root cause explanation with technical details

### Investigation Objectives
1. Specific objective
2. Technical validation
3. Solution implementation
```

### Section Organization
1. **Environment Setup** - imports și configurare
2. **Data Analysis** - investigație pas cu pas
3. **Problem Identification** - root cause
4. **Solution Implementation** - fix-ul propriu-zis
5. **Validation** - verificare că funcționează
6. **Executive Summary** - concluzii pentru management

## Code Standards

### Variable Naming
```python
# ✅ Clear business context
bronze_spec_result = spark.table(f"{BRONZE_PATH}.SPECIFICATION_RESULT")
silver_order_analysis = spark.table(f"{SILVER_PATH}.order_sample_analysis")

# ✅ Descriptive analysis objects
duplicate_columns = [col for col in all_columns if all_columns.count(col) > 1]
result_numeric_cols = [col for col in columns if 'RESULT_NUMERIC' in col.upper()]
```

### Output Display
```python
# ✅ Direct expression output
f"Bronze SPECIFICATION_RESULT loaded: {record_count:,} records"

# ✅ Dictionary for structured data
analysis_summary = {
    "layer": "Bronze",
    "records": bronze_count,
    "result_numeric_columns": result_cols
}
analysis_summary

# ✅ DataFrame display
results_df.show(truncate=False)
```

## Business Context Integration

### JIRA Integration
- **Ticket numbers** în header
- **Test cases** specifice
- **Environment** clar specificat
- **Problem statement** în business terms

### Documentation Standards
```python
# CRITICAL ISSUE IDENTIFIED: Clear description
# Root cause: Specific technical explanation
# Impact: Business impact description
# Location: Exact location in code/script

critical_issue = {
    "problem": "Duplicate column mapping",
    "severity": "HIGH",
    "impact": "Column conflict, data derivation failure",
    "location": "PySpark script final_df.select() section"
}
```

## Solution Implementation Pattern

### Problem → Investigation → Solution
1. **Identify** - what's wrong
2. **Analyze** - why it's wrong  
3. **Solve** - how to fix it
4. **Validate** - proof it works

### Example Fix Structure
```python
# CORRECTED SOLUTION: Description of fix
corrected_code = """
# Original problematic line:
# col('SR.RESULT_NUMERIC_TO').cast('decimal(38,2)').alias('RESULT_NUMERIC')

# CORRECTED: Proper column mapping
col('SR.RESULT_NUMERIC_TO').cast('decimal(38,2)').alias('RESULT_NUMERIC_TO')
"""
corrected_code
```

## Executive Summary Template

### Critical Findings
1. **Primary Issue**: Main technical problem
2. **Secondary Issues**: Related problems found

### Resolution Impact
- **Expected Result**: What should happen after fix
- **Test Case**: Which tests should pass
- **Business Value**: Why this matters

### Implementation Priority
1. **IMMEDIATE**: Critical fixes
2. **WEEK 1**: Important improvements
3. **WEEK 2**: Nice-to-have optimizations

## Best Practices Checklist

- [ ] No try-catch blocks hiding errors
- [ ] No print statements cluttering output  
- [ ] Clear variable names with business context
- [ ] One logical operation per cell
- [ ] Direct expressions for automatic output
- [ ] JIRA ticket and business context in header
- [ ] Problem statement clearly defined
- [ ] Root cause analysis with evidence
- [ ] Corrected solution provided
- [ ] Executive summary for stakeholders

## Anti-Patterns to Avoid

❌ **Silent Error Handling**
```python
try:
    df = spark.table("table")
except:
    pass  # Ascunde problema!
```

❌ **Print Statement Spam**
```python
print("Loading data...")
print(f"Count: {count}")
print("Done!")
```

❌ **Unclear Variable Names**
```python
df1 = spark.table("table1")
df2 = df1.join(df3)
result = df2.filter(col("x") > 5)
```

❌ **No Business Context**
```python
# Just code without explanation
final_df = df.select(col("A"), col("B"))
```

---

**Rezultat:** Un notebook Databricks profesional, curat, transparent, care identifică și rezolvă probleme fără să le ascundă, cu context business clar și soluții actionabile.