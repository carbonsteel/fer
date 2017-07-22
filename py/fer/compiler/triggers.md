
# trigger firing order

    on_realm_domain_import
    on_before_parse_realm
    + fullpath
    on_realm_path
    -> on_realm_domain_import
    on_domain_declaration_id

    on_after_parse_realm
    + imported
    on_compilation_done