from django.db import connection, models, transaction
from django.apps.registry import apps
from django.db.utils import IntegrityError

class CascadingUpdate():

    def get_fk_list(self, obj):
        for m in apps.get_models(include_auto_created=True):
            for f in m._meta.get_all_field_names():
                try:
                    relation = m._meta.get_field(f).rel
                except models.fields.FieldDoesNotExist:
                    continue
                if relation:
                    if relation.to == obj.__class__:
                        yield(m, f)



    def get_related_objects(self, obj, related_models):
        #returns an iterator of tuples (object, keyname)
        app_name = obj._meta.app_label
        for model_type, keyname in related_models:
            related_objects = model_type.objects.filter(**{keyname:obj})
            for r in related_objects:
                yield (r, keyname)



    def replace_related_keys(self, related_objects, obj, new_obj):
        if obj.__class__ != new_obj.__class__:
            raise AssertionError("Cannot merge objects of different classes")
        for related_obj, keyname in related_objects:
            #get new_obj's related objects of this type
            duplicate = False
            with transaction.atomic():
                setattr(related_obj, keyname, new_obj)
                try:    
                    related_obj.save()
                except IntegrityError:
                    duplicate = True
            if duplicate:
                related_obj.delete()


    def merge_foreign_keys(self, obj_to_remove, persistent_obj):
        fk_relations = self.get_fk_list(obj_to_remove)
        related_objects = self.get_related_objects(obj_to_remove, fk_relations)
        self.replace_related_keys(related_objects, obj_to_remove, persistent_obj)
