from django.test import TestCase
import tests
from .models import Person, Dog, Cat, Lion
from waterfall import CascadingUpdate

class SimpleMergeTest(TestCase):
    def setUp(self):
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        Dog.objects.create(name="fido", owner=zookeeper2)


    def test_simple_merge(self):
        #a related dog should be moved from one owner to another
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        dog = Dog.objects.filter(name="fido").first()
        self.assertEqual(dog.owner, zookeeper2)
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        dog = Dog.objects.filter(name="fido").first()
        self.assertEqual(dog.owner, zookeeper1)

class MergeWithExistingObjsTest(TestCase):
    def setUp(self):
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        Dog.objects.create(name="fido", owner=zookeeper2)
        Dog.objects.create(name="rex", owner=zookeeper1)

    def test_merge_with_existing_object(self):
        #a related dog should get moved, without causing
        #problems for an existing dog
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        fido = Dog.objects.filter(name="fido").first()
        self.assertEqual(fido.owner, zookeeper1)
        rex = Dog.objects.filter(name="rex").first()
        self.assertEqual(rex.owner, zookeeper1)

class MergeManyToManyTest(TestCase):
    def setUp(self):
        #a related cat should be moved.
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        cat1 = Cat.objects.create(name='fluffy')
        cat1.owners.add(zookeeper2)

    def test(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        fluffy = Cat.objects.filter(name="fluffy").first()
        self.assertIn(zookeeper1, fluffy.owners.all())
        self.assertNotIn(zookeeper2, fluffy.owners.all())
        self.assertIn(fluffy, zookeeper1.cat_set.all())
        self.assertNotIn(fluffy, zookeeper2.cat_set.all()) 

class MergeM2MWithExistingTest(TestCase):
    def setUp(self):
        #a related cat should be moved.
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        cat1 = Cat.objects.create(name='fluffy')
        cat2 = Cat.objects.create(name='whiskers')
        cat1.owners.add(zookeeper2)
        cat2.owners.add(zookeeper1)


    def test_merge_many_to_many_w_existing(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        whiskers = Cat.objects.filter(name="whiskers").first()
        fluffy = Cat.objects.filter(name="fluffy").first()
        self.assertIn(zookeeper1, whiskers.owners.all())
        self.assertIn(whiskers, zookeeper1.cat_set.all())
        self.assertIn(fluffy, zookeeper1.cat_set.all())
        self.assertIn(zookeeper1, fluffy.owners.all())
        self.assertEqual(zookeeper1.cat_set.count(), 2)
        self.assertEqual(zookeeper2.cat_set.count(), 0)

class MergeM2MWithIdenticalTest(TestCase):
    #if we try to merge two people who own the same cat
    #nothing fails and we get only one copy of the relationship
    #in the join table
    def setUp(self):
        #a related cat should be moved.
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        cat1 = Cat.objects.create(name='fluffy')
        cat1.owners.add(zookeeper2)
        cat1.owners.add(zookeeper1)
        cat2 = Cat.objects.create(name='whiskers')
        cat2.owners.add(zookeeper1)


    def test_merge_many_to_many_w_identical(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        fluffy = Cat.objects.filter(name="fluffy").first()
        whiskers = Cat.objects.filter(name="whiskers").first()
        self.assertIn(fluffy, zookeeper1.cat_set.all())
        self.assertEqual(zookeeper1.cat_set.count(), 2)
        self.assertEqual(fluffy.owners.count(), 1)
        self.assertIn(whiskers, zookeeper1.cat_set.all())

class MergeInheritedObj(TestCase):
    #an inherited obj with a second key to the same model works
    #when any configuration of keys is merged.
    def setUp(self):
        #a related cat should be moved.
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        zookeeper3 = Person.objects.create(name="zookeeper3")
        lion = Lion.objects.create(name="leo",
                                    lunch=zookeeper3)
        lion.owners.add(zookeeper2)

    def test_merge_inherited(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        zookeeper3 = Person.objects.filter(name="zookeeper3").first()
        c.merge_foreign_keys(zookeeper2, zookeeper1)
        leo = Lion.objects.filter(name="leo").first()
        self.assertIn(leo, zookeeper1.lion_set.all())
        self.assertIn(zookeeper1, leo.owners.all())
        self.assertEqual(zookeeper1.lion_set.filter(name='leo').first().lunch, zookeeper3)

    def test_second_foreign_key(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        zookeeper3 = Person.objects.filter(name="zookeeper3").first()
        c.merge_foreign_keys(zookeeper3, zookeeper1)
        leo = Lion.objects.filter(name="leo").first()
        self.assertEqual(leo.lunch, zookeeper1)

    def test_same_foreign_key(self):
        c = CascadingUpdate()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        zookeeper3 = Person.objects.filter(name="zookeeper3").first()
        c.merge_foreign_keys(zookeeper3, zookeeper2)
        leo = Lion.objects.filter(name="leo").first()
        self.assertEqual(leo.lunch, zookeeper2)
        self.assertEqual(leo.owners.first(), zookeeper2)

    def test_multiple_merges(self):
        c = CascadingUpdate()
        zookeeper1 = Person.objects.filter(name="zookeeper1").first()
        zookeeper2 = Person.objects.filter(name="zookeeper2").first()
        zookeeper3 = Person.objects.filter(name="zookeeper3").first()
        c.merge_foreign_keys(zookeeper3, zookeeper1)
        c.merge_foreign_keys(zookeeper1, zookeeper2)
        leo = Lion.objects.filter(name="leo").first()
        self.assertEqual(leo.lunch, zookeeper2)
        self.assertEqual(leo.owners.first(), zookeeper2)


class MergeRecursive(TestCase):
    def setUp(self):
        zookeeper1 = Person.objects.create(name="zookeeper1")
        zookeeper2 = Person.objects.create(name="zookeeper2")
        dog1 = Dog.objects.create(name="fido", owner=zookeeper2)
        Dog.objects.create(name="rex", owner=zookeeper1, parent_dog=dog1)
        Dog.objects.create(name="spot", owner=zookeeper1)

    def test_merge_with_recursive(self):
        #when a parent is merged, the child dog gets the new parent
        #note that with a 1-to-1 relationship we don't need to test
        #the other direction, because it's not a foreign key
        c = CascadingUpdate()
        fido = Dog.objects.filter(name="fido").first()
        spot = Dog.objects.filter(name="spot").first()
        c.merge_foreign_keys(fido, spot)
        rex = Dog.objects.filter(name="rex").first()
        self.assertEqual(rex.parent_dog,spot)

    def test_merge_to_own_parent(self):
        #the "I am my own grandpa" of test situations
        c = CascadingUpdate()
        fido = Dog.objects.filter(name="fido").first()
        rex = Dog.objects.filter(name="rex").first()
        c.merge_foreign_keys(fido, rex)
        rex = Dog.objects.filter(name="rex").first()
        self.assertEqual(rex.parent_dog,rex)



