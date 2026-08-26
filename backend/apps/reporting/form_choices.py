"""Controlled UI choices for analysable fields that are stored as plain text.

These choices standardise new data without requiring a database migration. Fields
that hold names, narrative explanations, identifiers, contacts, or exact locations
remain free text.
"""


def _choices(*values):
    return tuple((value, value.replace("_", " ").title()) for value in values)


COMMON_FIELD_CHOICES = {
    "gender": _choices("male", "female", "other", "unknown"),
    "victim_gender": _choices("male", "female", "mixed", "other", "unknown"),
    "owner_gender": _choices("male", "female", "other", "unknown"),
    "priority": _choices("low", "medium", "high", "urgent"),
    "severity": _choices("low", "moderate", "high", "severe", "critical"),
    "condition": _choices("excellent", "good", "fair", "poor", "unsafe", "destroyed", "under_construction"),
    "operational_status": _choices("operational", "partially_operational", "not_operational", "under_repair", "decommissioned"),
    "ownership": _choices("village", "community", "household", "government", "private", "faith_based", "other"),
    "primary_or_backup": _choices("primary", "backup"),
    "currency_code": (("FJD", "Fijian dollar (FJD)"), ("AUD", "Australian dollar (AUD)"), ("NZD", "New Zealand dollar (NZD)"), ("USD", "US dollar (USD)"), ("other", "Other")),
    "measurement_unit": _choices("people", "households", "cases", "incidents", "facilities", "count", "percentage", "litres", "hours", "days", "kilograms", "tonnes", "fijian_dollars", "other"),
    "collection_method": _choices("physical_count", "household census", "household_register", "document_review", "interview", "observation", "administrative_record", "community_estimate", "other"),
    "frequency": _choices("one_off", "daily", "weekly", "monthly", "quarterly", "seasonal", "annual", "rare", "other"),
    "risk_level": _choices("low", "medium", "high", "critical"),
    "funding_source": _choices("government", "provincial", "village", "donor", "ngo", "private", "community_contribution", "loan", "mixed", "other"),
}


MODEL_FIELD_CHOICES = {
    ("governance.OfficialAppointment", "confirmation_status"): _choices("pending", "confirmed", "disputed", "ended"),
    ("governance.MeetingDecision", "status"): _choices("not_started", "in_progress", "completed", "delayed", "cancelled"),
    ("governance.VillageVisit", "visit_type"): _choices("government", "health", "agriculture", "education", "project_monitoring", "disaster_response", "community_support", "other"),
    ("governance.VillageVisit", "follow_up_status"): _choices("not_required", "pending", "in_progress", "completed", "overdue"),
    ("governance.TrainingActivity", "category"): _choices("governance", "health", "agriculture", "livelihood", "finance", "climate_disaster", "culture", "digital_skills", "other"),
    ("governance.TrainingActivity", "delivery_method"): _choices("in_person", "online", "blended", "practical_demonstration", "other"),
    ("governance.TrainingActivity", "target_group"): _choices("whole_village", "leaders", "women", "youth", "farmers", "people_with_disability", "businesses", "other"),
    ("population.Household", "primary_livelihood"): _choices("subsistence_farming", "commercial_farming", "fishing", "formal_employment", "self_employment", "remittances", "social_support", "mixed", "other"),
    ("population.Household", "housing_type"): _choices("concrete", "timber", "corrugated_iron", "traditional", "mixed_material", "temporary", "other"),
    ("population.Household", "water_source"): _choices("piped_supply", "communal_tap", "rainwater", "borehole", "well", "spring", "river_stream", "bottled", "other"),
    ("population.Household", "toilet_type"): _choices("flush_septic", "flush_sewer", "pour_flush", "ventilated_pit", "pit_latrine", "composting", "none", "other"),
    ("population.Household", "energy_source"): _choices("grid_electricity", "solar", "generator", "battery", "kerosene", "none", "mixed", "other"),
    ("population.Household", "vulnerability_status"): _choices("none_identified", "elderly", "disability", "female_headed", "child_headed", "low_income", "disaster_exposed", "multiple", "other"),
    ("infrastructure.HousingSnapshot", "structure_type"): _choices("permanent_house", "semi_permanent_house", "traditional_house", "temporary_shelter", "other"),
    ("infrastructure.HousingSnapshot", "construction_material"): _choices("concrete", "timber", "corrugated_iron", "traditional_material", "mixed_material", "other"),
    ("infrastructure.HousingSnapshot", "occupancy_status"): _choices("occupied", "temporarily_vacant", "vacant", "abandoned", "under_construction"),
    ("infrastructure.VillageAsset", "asset_type"): _choices("community_hall", "office", "school", "health_facility", "vehicle", "boat", "equipment", "communications", "sports_facility", "other"),
    ("infrastructure.VillageWaterSource", "source_type"): _choices("piped_supply", "borehole", "well", "spring", "rainwater", "river_stream", "desalination", "other"),
    ("infrastructure.VillageWaterSource", "availability_status"): _choices("always_available", "seasonal", "intermittent", "unavailable"),
    ("infrastructure.VillageWaterSource", "water_quality_status"): _choices("safe", "requires_treatment", "unsafe", "not_tested", "unknown"),
    ("infrastructure.WaterInterruption", "resolution_status"): _choices("ongoing", "partially_restored", "resolved"),
    ("infrastructure.WaterQualityTest", "test_type"): _choices("microbiological", "chemical", "physical", "combined", "other"),
    ("infrastructure.WaterMaintenanceActivity", "activity_type"): _choices("inspection", "routine_maintenance", "repair", "replacement", "cleaning", "upgrade", "other"),
    ("infrastructure.WaterMaintenanceActivity", "completion_status"): _choices("planned", "in_progress", "completed", "delayed", "cancelled"),
    ("infrastructure.SanitationSnapshot", "toilet_type"): _choices("flush_septic", "flush_sewer", "pour_flush", "ventilated_pit", "pit_latrine", "composting", "none", "other"),
    ("infrastructure.WasteFacility", "facility_type"): _choices("landfill", "communal_dump", "transfer_station", "composting", "recycling", "burning_area", "other"),
    ("infrastructure.WasteFacility", "collection_frequency"): _choices("daily", "weekly", "fortnightly", "monthly", "on_demand", "none"),
    ("infrastructure.WasteFacility", "environmental_risk"): _choices("low", "medium", "high", "critical", "unknown"),
    ("infrastructure.WasteCollectionActivity", "waste_type"): _choices("general", "organic", "recyclable", "hazardous", "medical", "construction", "mixed", "other"),
    ("infrastructure.WasteCollectionActivity", "disposal_method"): _choices("landfill", "communal_dump", "recycling", "composting", "burning", "burial", "other"),
    ("infrastructure.EnergySnapshot", "energy_source"): _choices("grid_electricity", "solar", "generator", "hydro", "wind", "battery", "kerosene", "mixed", "other"),
    ("infrastructure.VillageEnergyAsset", "asset_type"): _choices("solar_system", "generator", "battery_bank", "mini_grid", "street_lighting", "other"),
    ("infrastructure.VillageEnergyAsset", "capacity_unit"): _choices("watts", "kilowatts", "kilowatt_hours", "units", "other"),
    ("infrastructure.VillageEnergyAsset", "fuel_or_energy_type"): _choices("solar", "diesel", "petrol", "hydro", "wind", "battery", "grid", "other"),
    ("wellbeing.CommunitySafetyIncident", "case_status"): _choices("not_reported", "reported", "under_investigation", "referred", "resolved", "closed", "unknown"),
    ("wellbeing.CommunitySafetyIncident", "authority_reported_to"): _choices("police", "village_leadership", "tikina", "provincial_office", "social_welfare", "health_authority", "other"),
    ("economy.CropProductionSnapshot", "area_unit"): _choices("square_metres", "hectares", "acres", "plots", "other"),
    ("economy.CropProductionSnapshot", "quantity_unit"): _choices("kilograms", "tonnes", "bundles", "bags", "pieces", "litres", "other"),
    ("economy.CropProductionSnapshot", "planting_season"): _choices("year_round", "wet_season", "dry_season", "seasonal", "other"),
    ("economy.VillageBusiness", "business_sector"): _choices("agriculture", "fisheries", "retail", "transport", "tourism", "construction", "services", "handicrafts", "food_processing", "other"),
    ("economy.VillageBusiness", "owner_type"): _choices("individual", "household", "cooperative", "women_group", "youth_group", "village", "company", "other"),
    ("economy.VillageBusiness", "licence_status"): _choices("not_required", "valid", "expired", "pending", "not_licensed", "unknown"),
    ("economy.VillageBusiness", "operating_status"): _choices("operating", "seasonal", "temporarily_closed", "permanently_closed", "planned"),
    ("economy.VillageBusiness", "revenue_band"): _choices("no_revenue", "under_5000", "5000_19999", "20000_49999", "50000_99999", "100000_or_more", "unknown"),
    ("economy.VillageBusiness", "primary_market"): _choices("village", "district", "provincial", "national", "export", "online", "mixed"),
    ("economy.VillageFinancialAccount", "account_type"): _choices("current", "savings", "fixed_deposit", "investment", "mobile_wallet", "other"),
    ("economy.VillageFinancialAccount", "account_purpose"): _choices("operations", "development_project", "emergency", "savings", "investment", "community_welfare", "other"),
    ("projects.IVDPProject", "project_category"): _choices("water", "sanitation", "energy", "housing", "health", "education", "livelihood", "transport", "climate_resilience", "culture", "governance", "other"),
    ("projects.IVDPProject", "project_status"): _choices("proposed", "approved", "not_started", "in_progress", "on_hold", "completed", "cancelled"),
    ("projects.ProjectMilestone", "status"): _choices("not_started", "in_progress", "completed", "delayed", "cancelled"),
    ("projects.ProjectRisk", "risk_type"): _choices("financial", "schedule", "technical", "environmental", "social", "procurement", "safety", "governance", "other"),
    ("projects.ProjectRisk", "likelihood"): _choices("rare", "unlikely", "possible", "likely", "almost_certain"),
    ("projects.ProjectRisk", "impact"): _choices("insignificant", "minor", "moderate", "major", "severe"),
    ("projects.ProjectRisk", "status"): _choices("open", "monitoring", "mitigated", "occurred", "closed"),
    ("resilience.ClimateImpactObservation", "hazard_type"): _choices("cyclone", "flood", "drought", "coastal_erosion", "sea_level_rise", "landslide", "extreme_heat", "saltwater_intrusion", "other"),
    ("resilience.EvacuationCentre", "building_material"): _choices("concrete", "timber", "steel", "mixed_material", "traditional_material", "other"),
    ("resilience.EvacuationCentre", "accessibility_status"): _choices("fully_accessible", "partially_accessible", "not_accessible", "unknown"),
    ("resilience.DisasterIncident", "incident_type"): _choices("cyclone", "flood", "drought", "landslide", "fire", "earthquake", "tsunami", "disease_outbreak", "other"),
    ("culture.TraditionalTitle", "title_type"): _choices("chiefly", "clan", "family", "ceremonial", "other"),
    ("culture.TraditionalTitle", "status"): _choices("occupied", "vacant", "acting", "disputed", "under_confirmation"),
    ("culture.CulturalKnowledgeRecord", "knowledge_category"): _choices("oral_history", "traditional_ceremony", "language", "medicine", "fishing", "farming", "craft", "dance_music", "navigation", "other"),
    ("culture.CulturalKnowledgeRecord", "transmission_status"): _choices("actively_transmitted", "occasionally_transmitted", "not_currently_transmitted", "unknown"),
    ("culture.CulturalKnowledgeRecord", "activity_frequency"): _choices("weekly", "monthly", "quarterly", "seasonal", "annual", "occasional", "none"),
    ("documents.EvidenceDocument", "document_type"): _choices("register", "meeting_minutes", "photograph", "official_letter", "survey", "receipt_invoice", "plan", "map", "other"),
}


def controlled_choices(model, field_name):
    return MODEL_FIELD_CHOICES.get((model._meta.label, field_name), COMMON_FIELD_CHOICES.get(field_name))
