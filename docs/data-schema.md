# Open Data Schemas — Development Priority Intelligence

All data entities used in Development Priority Intelligence conform to open JSON Schema standards to uphold **Digital Public Good (DPG)** principles.

---

## 1. Citizen Request Schema (`CitizenRequest`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CitizenRequest",
  "type": "object",
  "required": [
    "id",
    "timestamp",
    "raw_text",
    "source_channel",
    "detected_language",
    "category",
    "admin_hierarchy",
    "data_quality"
  ],
  "properties": {
    "id": { "type": "string", "description": "Unique identifier (UUID)" },
    "timestamp": { "type": "string", "format": "date-time" },
    "raw_text": { "type": "string", "description": "Original citizen submission" },
    "translated_text": { "type": "string", "description": "Normalized English intent translation" },
    "source_channel": { 
      "type": "string", 
      "enum": ["voice_web_speech", "text_web_portal", "messaging_app", "sms", "field_survey"] 
    },
    "detected_language": { "type": "string", "example": "mr" },
    "category": { 
      "type": "string", 
      "enum": ["healthcare", "water_sanitation", "roads_transport", "education", "electricity"] 
    },
    "sub_category": { "type": "string", "example": "phc_shortage" },
    "urgency_level": { "type": "string", "enum": ["low", "medium", "high", "critical"] },
    "photo_evidence_url": { "type": ["string", "null"] },
    "admin_hierarchy": {
      "type": "object",
      "required": ["country_code", "admin1", "admin2"],
      "properties": {
        "country_code": { "type": "string", "example": "IND" },
        "admin1": { "type": "string", "example": "Maharashtra" },
        "admin2": { "type": "string", "example": "Pune" },
        "admin3": { "type": "string", "example": "Haveli" },
        "locality": { "type": "string", "example": "Khed Shivapur" },
        "latitude": { "type": ["number", "null"] },
        "longitude": { "type": ["number", "null"] }
      }
    },
    "cluster_id": { "type": ["string", "null"], "description": "Semantic cluster assigned by Gemini" },
    "data_quality": {
      "type": "string",
      "enum": ["real", "synthetic"],
      "description": "Indicates whether record is from real ingestion or synthetic test suite"
    }
  }
}
```

---

## 2. Infrastructure Inventory Schema (`InfrastructureInventory`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InfrastructureInventory",
  "type": "object",
  "required": [
    "facility_id",
    "name",
    "category",
    "facility_type",
    "admin_hierarchy",
    "status",
    "source",
    "retrieved_at"
  ],
  "properties": {
    "facility_id": { "type": "string" },
    "name": { "type": "string" },
    "category": { "type": "string", "enum": ["healthcare", "water_sanitation", "roads_transport", "education"] },
    "facility_type": { "type": "string", "example": "Community Health Centre (CHC)" },
    "admin_hierarchy": {
      "type": "object",
      "properties": {
        "country_code": { "type": "string", "example": "IND" },
        "admin1": { "type": "string", "example": "Maharashtra" },
        "admin2": { "type": "string", "example": "Pune" },
        "latitude": { "type": "number" },
        "longitude": { "type": "number" }
      }
    },
    "operational_capacity": { "type": "object", "additionalProperties": true },
    "status": { "type": "string", "enum": ["operational", "under_repair", "abandoned", "planned"] },
    "source": { "type": "string", "example": "National Hospital Directory (data.gov.in)" },
    "source_url": { "type": "string" },
    "retrieved_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 3. Public Investment & Projects Schema (`GovernmentProject`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GovernmentProject",
  "type": "object",
  "required": [
    "project_id",
    "title",
    "sector",
    "admin_hierarchy",
    "budget_amount",
    "currency",
    "status",
    "source",
    "retrieved_at"
  ],
  "properties": {
    "project_id": { "type": "string" },
    "title": { "type": "string" },
    "sector": { "type": "string" },
    "admin_hierarchy": { "type": "object" },
    "budget_amount": { "type": "number" },
    "currency": { "type": "string", "example": "INR" },
    "status": { "type": "string", "enum": ["Announced", "Ongoing", "Completed", "Stalled"] },
    "start_date": { "type": "string", "format": "date" },
    "completion_date": { "type": ["string", "null"], "format": "date" },
    "source": { "type": "string" },
    "retrieved_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 4. Priority Score & Recommendation Schema (`PriorityScoreResult`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PriorityScoreResult",
  "type": "object",
  "required": [
    "region_id",
    "sector",
    "priority_score",
    "score_components",
    "silent_need_flag",
    "mismatch_flag",
    "grounded_explanation"
  ],
  "properties": {
    "region_id": { "type": "string" },
    "sector": { "type": "string" },
    "priority_score": { "type": "number", "minimum": 0, "maximum": 100 },
    "rank": { "type": "integer" },
    "score_components": {
      "type": "object",
      "properties": {
        "demand_score": { "type": "number" },
        "population_affected": { "type": "integer" },
        "infra_deficit_score": { "type": "number" },
        "existing_investment_inr_cr": { "type": "number" }
      }
    },
    "silent_need_flag": { "type": "boolean" },
    "mismatch_flag": { "type": "string", "enum": ["none", "underfunded_hotspot", "ineffective_expenditure"] },
    "grounded_explanation": { "type": "string" }
  }
}
```

---

## 5. Impact Measurement Schema (`ImpactMeasurementResult`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ImpactMeasurementResult",
  "type": "object",
  "required": [
    "project_id",
    "completion_date",
    "pre_complaints_count",
    "post_complaints_count",
    "impact_percentage",
    "verification_status"
  ],
  "properties": {
    "project_id": { "type": "string" },
    "project_name": { "type": "string" },
    "completion_date": { "type": "string", "format": "date" },
    "observation_window_days": { "type": "integer", "default": 180 },
    "pre_complaints_count": { "type": "integer" },
    "post_complaints_count": { "type": "integer" },
    "impact_percentage": { "type": "number", "description": "Positive value indicates reduction in complaints" },
    "pre_priority_score": { "type": "number" },
    "post_priority_score": { "type": "number" },
    "verification_status": { 
      "type": "string", 
      "enum": ["Verified Reduction", "Marginal Impact", "Persistent Deficit", "Insufficient Post-Data"] 
    },
    "data_disclaimer": { 
      "type": "string", 
      "default": "Based on available post-commissioning reporting data; not a guaranteed forecast." 
    }
  }
}
```
