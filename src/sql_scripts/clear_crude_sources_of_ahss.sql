--- get from specific project the crude data of the sources of the AHSS ---
--- use only id and name of the source for min tokens ---
--- we want this so AI will determine which are the best sources to use based on topic of the project ---

SELECT
    pm.id,
    pm.title
FROM
    ai_schema.papers_metadata pm
WHERE
    project_name = 'Panos_Karydis'