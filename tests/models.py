from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=20)

class Dog(models.Model):
    name = models.CharField(max_length=20)
    owner = models.ForeignKey(Person) #test many to one
    parent_dog = models.ForeignKey('self', blank=True, null=True) #test relationship to same obj

class Feline(models.Model):
    name = models.CharField(max_length=20)
    owners = models.ManyToManyField(Person)
    class Meta:
        abstract = True

class Cat(Feline):
     #test many to many
     pass

class Lion(Feline):
    lunch = models.ForeignKey(Person, related_name='eaten_by') #check inheritence
