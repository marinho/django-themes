import app_settings

_registered_templates = {}

def register_template(name, **kwargs):
    """
    Function responsible to register a template in the _registered_templates dictionary.

    Once a template is registered, the template loader recognizes it and controls its
    permissions and available stuff.

    The recognized named arguments are:

        - verbose_name          - Default: assumes the name
        - default_base_template - Default: assumes app_settings.BASE_TEMPLATE
        - mirroring             - Default: assumes empty
        - available_blocks      - Default: assumes empty
        - available_vars        - Default: assumes empty
        - available_loads       - Default: assumes app_settings.AVAILABLE_LOADS
        - available_tags        - Default: assumes app_settings.AVAILABLE_TAGS
        - available_filters     - Default: assumes app_settings.AVAILABLE_FILTERS
        - available_includes    - Default: assumes app_settings.AVAILABLE_INCLUDES
        - excluded_vars         - Default: assumes none (that means all of them are accessible
    """
    kwargs['name'] = name
    _registered_templates[name] = kwargs

def get_registered_template(name, *args):
    return _registered_templates.get(name, *args)

def list_registered_templates():
    return _registered_templates.items()

