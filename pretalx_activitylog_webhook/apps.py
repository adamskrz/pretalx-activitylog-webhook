from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_activitylog_webhook"
    verbose_name = "ActivityLog Webhook"

    class PretalxPluginMeta:
        name = gettext_lazy("ActivityLog Webhook")
        author = "Adam Skrzymowski"
        description = gettext_lazy("pretalx plugin for ActivityLog Webhook")
        visible = True
        version = __version__
        category = "INTEGRATION"

    def ready(self):
        from . import signals  # NOQA
