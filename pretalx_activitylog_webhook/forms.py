
from i18nfield.forms import I18nModelForm

from .models import ActivitylogWebhookSettings


class ActivitylogWebhookSettingsForm(I18nModelForm):

    def __init__(self, *args, event=None, **kwargs):
        self.instance, _ = ActivitylogWebhookSettings.objects.get_or_create(event=event)
        super().__init__(*args, **kwargs, instance=self.instance, locales=event.locales)

    class Meta:
        model = ActivitylogWebhookSettings
        fields = ("some_setting", )
        widgets = {}

