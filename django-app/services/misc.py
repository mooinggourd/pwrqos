import math
from itertools import chain
from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from cgi import escape

class ColumnCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, columns=2, css_class=None, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.columns = columns
        self.css_class = css_class

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        choices_enum = list(enumerate(chain(self.choices, choices)))
        
        output = []
        if self.css_class:
            output.append(u'<table class="%s">' % self.css_class)
        else:
            output.append(u'<table>')

        str_values = set([force_unicode(v) for v in value])                        
        for i, (option_value, option_label) in choices_enum:
            if i % self.columns == 0:
                output.append(u'<tr>')
        
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (
                        attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
        
            cb = forms.CheckboxInput(
                final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<td><label%s>%s</label>%s</td>' % (
                    label_for, option_label, rendered_cb))
        
            if i % self.columns == self.columns - 1:
                output.append(u'</tr>')
        
        output.append(u'</table>')
        
        return mark_safe(u'\n'.join(output))        

class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, *args, **kwargs):
        self.class_name = kwargs.pop('class_name', None)
        super(forms.CheckboxSelectMultiple, self).__init__(*args, **kwargs)
              
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)
        if self.class_name:
            return mark_safe(html.replace('<ul>', '<ul class="%s">' % self.class_name))
        else:
            return html       

class ServiceMultipleModelChoiceField(forms.models.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return mark_safe('<span class="service-name"><a href="/services/%d/">%s</a></span><span class="service-desc">%s</span>' % (obj.pk, 
            escape(obj.name), 
            escape(obj.description)))
