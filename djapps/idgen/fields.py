
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.forms import fields as djfields
from django.core.exceptions import ValidationError
import api as idgenapi

class StringIDFormField(djfields.CharField):
    def __init__(self, *args, **kwargs):
        idgen = kwargs.get("idgen")
        key_length = kwargs.get("max_length", 0)
        assert idgen != None, "%ss must have a valid id_genfunc field value" % self.__class__.__name__
        assert key_length and key_length > 0, "%ss must have a positive key_length" % self.__class__.__name__
        self.key_length = key_length
        self.id_genfunc = idgen
        del kwargs["idgen"]
        super(StringIDFormField, self).__init__(*args, **kwargs)

    def validate(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises ValidationError for any errors.
        """
        super(StringIDFormField, self).validate(value)
        if value:
            value = value.strip()
            if type(self.id_genfunc) in (str, unicode):
                idgenapi.validate_id(self.id_genfunc, value)
                if idgenapi.is_id_used(self.id_genfunc, value):
                    raise ValidationError("ID '%s' is already in use." % value)
            else:
                print >> sys.stderr, "GenFuncs that are not strings cannot be validated"
                # otherwise it is a function so call it and call the next
                # id on the returned the idgen as we could have runtime
                # idgens
                # if idgenapi.is_id_used(self.id_genfunc(model_instance), value):
                    # raise ValidationError("ID '%s' is already taken." % value)
        return value

class StringIDField(models.CharField):
    """
    A field that can be used to provide random IDs.
    """
    description = _("A field that can create random IDs using an id generator.")

    def __init__(self, idgen, key_length, *args, **kwargs):
        assert idgen != None, "%ss must have a valid idgen field value" % self.__class__.__name__
        assert key_length and key_length > 0, "%ss must have a positive key_length" % self.__class__.__name__
        self.id_genfunc = idgen
        self.id_generator = None
        self.key_length = key_length
        self.initialised = False
        kwargs['max_length'] = key_length
        super(StringIDField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Returns field's value just before saving.
        """
        if add: # new instance so create a new ID value
            # if the idgen is a string then we can use it as is
            value = getattr(model_instance, self.attname)
            if value is not None: value = value.strip()
            if type(self.id_genfunc) in (str, unicode):
                if value and not idgenapi.mark_id_as_used(self.id_genfunc, value):
                    raise ValueError("ID '%s' is already taken." % value)
                elif not value:
                    value = idgenapi.get_next_id(self.id_genfunc)
            else:
                # otherwise it is a function so call it and call the next
                # id on the returned the idgen as we could have runtime
                # idgens
                if value and not idgenapi.mark_id_as_used(self.id_genfunc(model_instance), value):
                    raise ValueError("ID '%s' is already taken." % value)
                elif not value:
                    value = idgenapi.get_next_id(self.id_genfunc(model_instance))
            setattr(model_instance, self.attname, value)
            return value 
        else:
            return super(StringIDField, self).pre_save(model_instance, add)

    def formfield(self, **kwargs):
        defaults = {'form_class': StringIDFormField,
                     'required': False,
                     'idgen': self.id_genfunc,
                     'max_length': self.key_length}
        defaults.update(kwargs)
        return super(StringIDField, self).formfield(**defaults)

# allow South to handle StringIDField smoothly
try:
    from south.modelsinspector import add_introspection_rules
    # For a normal StringIDField, the add_rendered_field attribute is
    # always True, which means no_rendered_field arg will always be
    # True in a frozen StringIDField, which is what we want.
    add_introspection_rules(rules=[((StringIDField,), [], {})],
                            patterns=['djapps\.idgen\.fields\.'])
except ImportError:
    pass

