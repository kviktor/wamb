from django import forms
from django.urls import reverse


class AutocompleteSelectMultiple(forms.SelectMultiple):
    """Select rendered as beercss chips, options are searched with the
    autocomplete endpoint. Only the selected options are rendered."""

    class Media:
        css = {"all": ["css/autocomplete-select.css"]}
        # deferred like htmx, the init script needs htmx.onLoad
        js = [
            forms.Script("js/choices.min.js", defer=True),
            forms.Script("js/autocomplete-select.js", defer=True),
        ]

    def __init__(self, model, attrs=None):
        super().__init__(attrs)
        self.model = model

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["data-autocomplete-url"] = reverse("autocomplete")
        context["widget"]["attrs"]["data-autocomplete-model"] = self.model
        return context

    def optgroups(self, name, value, attrs=None):
        # rendering every option would load the whole table, the field still
        # validates against the full queryset
        field = self.choices.field
        options = []
        selected = field.queryset.filter(pk__in=[v for v in value if v.isdigit()])
        for obj in selected:
            options.append(
                self.create_option(
                    name,
                    obj.pk,
                    field.label_from_instance(obj),
                    True,
                    len(options),
                    attrs=attrs,
                )
            )

        return [(None, options, 0)]
