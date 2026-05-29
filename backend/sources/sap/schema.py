# SAP ingestion schema and aliases.

EXPECTED_COLUMNS = ["date", "plant", "kgCO2e", "unit", "scope"]

COLUMN_ALIASES = {
	"amount": ["kgco2e", "co2e_kg", "emission", "emission_value", "amount"],
	"unit": ["unit", "uom", "measure", "einheit"],
	"period": ["date", "posting_date", "buchungsdatum", "period", "datum"],
	"scope": ["scope", "ghg_scope", "scope_number", "emissions_scope"],
	"plant_code": ["plant", "plant_code", "werk", "werks", "plantid"],
}

DATE_FORMATS = ["%d.%m.%Y", "%Y%m%d", "%Y-%m-%d", "%d/%m/%Y"]

UNIT_ALIASES = {
	"kgco2e": "kgCO2e",
	"k gco2e": "kgCO2e",
	"kg co2e": "kgCO2e",
	"tco2e": "tCO2e",
	"t co2e": "tCO2e",
	"gco2e": "gCO2e",
}

SCOPE_ALIASES = {
	"1": "scope_1",
	"2": "scope_2",
	"3": "scope_3",
	"scope 1": "scope_1",
	"scope 2": "scope_2",
	"scope 3": "scope_3",
	"scope_1": "scope_1",
	"scope_2": "scope_2",
	"scope_3": "scope_3",
}
