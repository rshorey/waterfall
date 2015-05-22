from django.db import connection, models

class CascadingUpdate():
    
    def __init__(self):
        self.table_modelnames = self.get_table_modelnames()

    def get_table_modelnames(self):
        table_modelnames = {}
        for m in models.get_models():
            table_modelnames[m._meta.db_table] = m
        return table_modelnames

    def get_fk_list(self, obj):
        cursor = connection.cursor()
        update_cursor = connection.cursor()
        table_name = obj._meta.db_table
        sql = """select s_class.relname source_table,
                att.attname source_name
                from pg_constraint cons join pg_class f_class
                on cons.confrelid = f_class.oid
                join pg_class s_class
                on cons.conrelid = s_class.oid
                join pg_attribute att
                on att.attnum = ANY (cons.conkey)
                and att.attrelid = s_class.oid
                where f_class.relname = %s
                and cons.contype = 'f'"""

        cursor.execute(sql, [table_name])
        return cursor

    def get_related_objects(self, obj, related_tables):
        #returns an iterator of tuples (object, keyname)
        app_name = obj._meta.app_label
        for table, keyname in related_tables:
            model_type = self.table_modelnames[table]
            related_objects = model_type.objects.filter(**{keyname:obj.id})
            for r in related_objects:
                yield (r, keyname)


    def replace_related_keys(self, related_objects, obj, new_obj):
        #make sure the objects are of the same type before doing anything
        if obj.__class__ != new_obj.__class__:
            raise AssertionError("Cannot merge objects of different classes")
        for related_obj, keyname in related_objects:
            setattr(related_obj, keyname, new_obj.id)
            related_obj.save()


    def merge_foreign_keys(self, obj_to_remove, persistent_obj):
        fk_relations = self.get_fk_list(obj_to_remove)
        related_objects = self.get_related_objects(obj_to_remove, fk_relations)
        self.replace_related_keys(related_objects, obj_to_remove, persistent_obj)