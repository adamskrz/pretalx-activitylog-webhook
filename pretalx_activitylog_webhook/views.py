from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from pretalx.common.views.mixins import PermissionRequired

from .forms import WebhookFormSet

class ActivitylogWebhookSettingsView(PermissionRequired, FormView):
    permission_required = "event.update_event"
    template_name = "pretalx_activitylog_webhook/settings.html"
    form_class = WebhookFormSet

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return self.request.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs["event"] = self.request.event
        kwargs["instance"] = self.get_object()
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        # Pass POST data to the formset during validation
        result = self.form_valid(form) if form.is_valid() else self.form_invalid(form)
        return result

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("The pretalx ActvityLog webhook plugin settings were updated."))
        return super().form_valid(form)
