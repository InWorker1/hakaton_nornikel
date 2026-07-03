
CREATE CONSTRAINT material_id_unique      IF NOT EXISTS FOR (n:Material)    REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT process_id_unique       IF NOT EXISTS FOR (n:Process)     REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT equipment_id_unique     IF NOT EXISTS FOR (n:Equipment)   REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT property_id_unique      IF NOT EXISTS FOR (n:Property)    REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT experiment_id_unique    IF NOT EXISTS FOR (n:Experiment)  REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT publication_id_unique   IF NOT EXISTS FOR (n:Publication) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT expert_id_unique        IF NOT EXISTS FOR (n:Expert)      REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT facility_id_unique      IF NOT EXISTS FOR (n:Facility)    REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT condition_id_unique     IF NOT EXISTS FOR (n:Condition)   REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT material_slug_unique    IF NOT EXISTS FOR (n:Material)    REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT process_slug_unique     IF NOT EXISTS FOR (n:Process)     REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT equipment_slug_unique   IF NOT EXISTS FOR (n:Equipment)   REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT property_slug_unique    IF NOT EXISTS FOR (n:Property)    REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT experiment_slug_unique  IF NOT EXISTS FOR (n:Experiment)  REQUIRE n.slug IS UNIQUE;
CREATE CONSTRAINT condition_slug_unique   IF NOT EXISTS FOR (n:Condition)   REQUIRE n.slug IS UNIQUE;

CREATE CONSTRAINT publication_doi_unique  IF NOT EXISTS FOR (n:Publication) REQUIRE n.doi IS UNIQUE;
CREATE CONSTRAINT expert_orcid_unique     IF NOT EXISTS FOR (n:Expert)      REQUIRE n.orcid IS UNIQUE;

CREATE INDEX material_name_ru             IF NOT EXISTS FOR (n:Material)    ON (n.name_i18n_ru);
CREATE INDEX material_name_en             IF NOT EXISTS FOR (n:Material)    ON (n.name_i18n_en);
CREATE INDEX process_name_ru              IF NOT EXISTS FOR (n:Process)     ON (n.name_i18n_ru);
CREATE INDEX process_name_en              IF NOT EXISTS FOR (n:Process)     ON (n.name_i18n_en);
CREATE INDEX equipment_name_ru            IF NOT EXISTS FOR (n:Equipment)   ON (n.name_i18n_ru);
CREATE INDEX equipment_name_en            IF NOT EXISTS FOR (n:Equipment)   ON (n.name_i18n_en);
CREATE INDEX property_name_ru             IF NOT EXISTS FOR (n:Property)    ON (n.name_i18n_ru);
CREATE INDEX property_name_en             IF NOT EXISTS FOR (n:Property)    ON (n.name_i18n_en);
CREATE INDEX experiment_name_ru           IF NOT EXISTS FOR (n:Experiment)  ON (n.name_i18n_ru);
CREATE INDEX experiment_name_en           IF NOT EXISTS FOR (n:Experiment)  ON (n.name_i18n_en);
CREATE INDEX publication_name_ru          IF NOT EXISTS FOR (n:Publication) ON (n.name_i18n_ru);
CREATE INDEX publication_name_en          IF NOT EXISTS FOR (n:Publication) ON (n.name_i18n_en);
CREATE INDEX expert_name_ru               IF NOT EXISTS FOR (n:Expert)      ON (n.name_i18n_ru);
CREATE INDEX expert_name_en               IF NOT EXISTS FOR (n:Expert)      ON (n.name_i18n_en);
CREATE INDEX facility_name_ru             IF NOT EXISTS FOR (n:Facility)    ON (n.name_i18n_ru);
CREATE INDEX facility_name_en             IF NOT EXISTS FOR (n:Facility)    ON (n.name_i18n_en);
CREATE INDEX condition_name_ru            IF NOT EXISTS FOR (n:Condition)   ON (n.name_i18n_ru);
CREATE INDEX condition_name_en            IF NOT EXISTS FOR (n:Condition)   ON (n.name_i18n_en);

CREATE INDEX publication_year             IF NOT EXISTS FOR (n:Publication) ON (n.year);
CREATE INDEX experiment_started_at        IF NOT EXISTS FOR (n:Experiment)  ON (n.started_at);
CREATE INDEX facility_country             IF NOT EXISTS FOR (n:Facility)    ON (n.country);
CREATE INDEX material_cas_number          IF NOT EXISTS FOR (n:Material)    ON (n.cas_number);
CREATE INDEX condition_kind               IF NOT EXISTS FOR (n:Condition)   ON (n.kind);
CREATE INDEX expert_current               IF NOT EXISTS FOR (n:Expert)      ON (n.current);

CREATE FULLTEXT INDEX material_search_text   IF NOT EXISTS FOR (n:Material)    ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX process_search_text    IF NOT EXISTS FOR (n:Process)     ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX equipment_search_text  IF NOT EXISTS FOR (n:Equipment)   ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX property_search_text   IF NOT EXISTS FOR (n:Property)    ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX experiment_search_text IF NOT EXISTS FOR (n:Experiment)  ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX publication_search_text IF NOT EXISTS FOR (n:Publication) ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX expert_search_text     IF NOT EXISTS FOR (n:Expert)      ON EACH [n.aliases, n.tags, n.email];
CREATE FULLTEXT INDEX facility_search_text   IF NOT EXISTS FOR (n:Facility)    ON EACH [n.aliases, n.tags];
CREATE FULLTEXT INDEX condition_search_text  IF NOT EXISTS FOR (n:Condition)   ON EACH [n.aliases, n.tags];

CREATE INDEX rel_confidence_uses_material         IF NOT EXISTS FOR ()-[r:uses_material]-()         ON (r.confidence);
CREATE INDEX rel_confidence_operates_at_condition IF NOT EXISTS FOR ()-[r:operates_at_condition]-() ON (r.confidence);
CREATE INDEX rel_confidence_produces_output       IF NOT EXISTS FOR ()-[r:produces_output]-()       ON (r.confidence);
CREATE INDEX rel_source_date_described_in         IF NOT EXISTS FOR ()-[r:described_in]-()         ON (r.source_date);
CREATE INDEX rel_validity_validated_by            IF NOT EXISTS FOR ()-[r:validated_by]-()         ON (r.valid_from, r.valid_to);

/*
CREATE CONSTRAINT xxx_id_unique    IF NOT EXISTS FOR (n:Xxx) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT xxx_slug_unique  IF NOT EXISTS FOR (n:Xxx) REQUIRE n.slug IS UNIQUE;
CREATE INDEX      xxx_name_ru      IF NOT EXISTS FOR (n:Xxx) ON (n.name_i18n_ru);
CREATE INDEX      xxx_name_en      IF NOT EXISTS FOR (n:Xxx) ON (n.name_i18n_en);
CREATE FULLTEXT INDEX xxx_search_text IF NOT EXISTS FOR (n:Xxx) ON EACH [n.aliases, n.tags];
*/
