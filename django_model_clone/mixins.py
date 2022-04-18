from copy import deepcopy

class ModelCloneUtil:
    clone_objects_set = []
    search_count = 0


class CloneObjectSet:
    def __init__(self, original_object, cloned_object) -> None:
        self.original_object = original_object
        self.cloned_object = cloned_object


class CloneMixin:
    # Included Fields
    _clone_many_to_many_related_fields = []
    _clone_related_fields = []

    def clone(self):
        self.cloned_object = deepcopy(self)
        self.cloned_object.pk = None
        self.cloned_object.save()
        ModelCloneUtil.clone_objects_set.append(CloneObjectSet(self, self.cloned_object))
        ModelCloneUtil.search_count += 1
        self.get_cloned_related_objects()
        ModelCloneUtil.search_count -= 1
        if ModelCloneUtil.search_count == 0:
            ModelCloneUtil.clone_objects_set = []
        return self.cloned_object

    def get_cloned_related_objects(self):
        for related_field_str in self._clone_many_to_many_related_fields:
            self.search_many_to_many_field(related_field_str)

        for related_field_str in self._clone_related_fields:
            self.search_relation_field(related_field_str)

    def get_cloned_object(self, model_object):
        for clone_object_set in ModelCloneUtil.clone_objects_set:
            if clone_object_set.original_object == model_object:
                return clone_object_set.cloned_object

        cloned_object = model_object.clone()
        ModelCloneUtil.clone_objects_set.append(CloneObjectSet(model_object, cloned_object))
        return cloned_object

    def search_many_to_many_field(self, related_field_str):
        related_field = getattr(self, related_field_str)
        for related_object in related_field.all():
            cloned_object = self.get_cloned_object(related_object)
            getattr(self.cloned_object, related_field_str).add(cloned_object)
            cloned_object.save()

    def search_relation_field(self, related_field_str):
        related_field = getattr(self, related_field_str)
        for related_object in related_field.all():
            cloned_object = self.get_cloned_object(related_object)
            setattr(cloned_object, related_field.field.attname, self.cloned_object.id)
            cloned_object.save()
