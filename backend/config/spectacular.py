def deduplicate_required_fields(result, generator, request, public):
    """
    Hook de post-traitement pour drf-spectacular.
    Élimine les doublons dans les listes 'required' des schémas OpenAPI
    après la conversion camelCase (requis pour la conformité OpenAPI uniqueItems=True).
    """
    if generator and hasattr(generator, 'registry'):
        for (_, component_type), component in generator.registry._components.items():
            if component_type == 'schemas':
                schema = component.schema
                if isinstance(schema, dict) and 'required' in schema:
                    schema['required'] = list(dict.fromkeys(schema['required']))

    schemas = result.get('components', {}).get('schemas', {})
    for s in schemas.values():
        if isinstance(s, dict) and 'required' in s:
            s['required'] = list(dict.fromkeys(s['required']))

    return result
