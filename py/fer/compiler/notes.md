
# plugin loader

    ALERTER_ENV_NAME = "ALERTER_PATH"
    TEMPLATES_PATH = os.getenv(ALERTER_ENV_NAME, "./alerter.d")
    TEMPLATES = None
    TEMPLATE_EXPORT_VARNAME = "alerter_export_templates"
    @classmethod
    def get_templates(cls):
        if cls.TEMPLATES is None:
            cls.load_templates()
        return ["%s.%s" % (module_name, f_name,) for module_name in cls.TEMPLATES for f_name in cls.TEMPLATES[module_name]]
    @classmethod
    def load_templates(cls):
        #loglib.log_init(__name__, True)
        #loglib.log_set_level(loglib.log_level.DEBUG)
        loglib.debug("Loading templates")
        sys.path.append(cls.TEMPLATES_PATH)
        try:
            cls.TEMPLATES = {}
            for module_path in glob.glob(cls.TEMPLATES_PATH + "/*"):
                try:
                    module_dir, module_file = os.path.split(module_path)
                    module_name, module_ext = os.path.splitext(module_file)
                    if module_ext != ".py":
                        continue
                    loglib.debug("Found candidate at %s" % (module_path,))
                    loglib.debug("Importing %s" % (module_name,))
                    template_module = __import__(module_name)
                    if hasattr(template_module, cls.TEMPLATE_EXPORT_VARNAME):
                        cls.TEMPLATES[template_module.__name__] = getattr(template_module, cls.TEMPLATE_EXPORT_VARNAME)
                        loglib.debug("Templates from module loaded")
                    else:
                        raise ValueError("module %s does not contain member %s" % (module_path, cls.TEMPLATE_EXPORT_VARNAME,))
                except Exception:
                    loglib.error(
                            "Cannot import templates from module at %s" % (module_path,),
                            exc_info=True)
                    raise
        except Exception:
            loglib.error(
                    "Failed to load templates",
                    exc_info=True)
            cls.TEMPLATES = None
            raise
        else:
            loglib.debug("Loaded %d modules" % (len(cls.TEMPLATES),))