
from django.utils.translation import ugettext_lazy as _
from django.db import models
import api as idgenapi

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
            if type(self.id_genfunc) in (str, unicode):
                value = idgenapi.get_next_id(self.id_genfunc)
            else:
                # otherwise it is a function so call it and call the next
                # id on the returned the idgen as we could have runtime
                # idgens
                value = idgenapi.get_next_id(self.id_genfunc(model_instance))
            setattr(model_instance, self.attname, value)
            return value 
        else:
            return super(StringIDField, self).pre_save(model_instance, add)

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

