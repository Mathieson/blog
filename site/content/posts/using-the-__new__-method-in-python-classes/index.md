+++
title = "Using the __new__ method in Python classes"
date = 2021-03-28T00:00:00Z
tags = ["python"]
+++


The \_\_new\_\_ method is a special method for Python classes. It is essentially the constructor for your class and handles its creation. You may think this is what the \_\_init\_\_ method is for, but the class instance (referred to from here out as "object") is actually already created by the time \_\_init\_\_ gets called. The \_\_init\_\_ method is just setting initial values for an already created object. The \_\_new\_\_ method is what gets called before the object exists and actually creates and returns the object.

This concept can be a bit confusing at first. A better way of understanding might be through example.

```
class Sphere(object):
    pass

class Cube(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(Sphere, *args, **kwargs)

obj = Cube()
print "My cube object is of type: %s" % type(obj)
```

Here is the most basic and obvious example of what \_\_new\_\_ does. If you run this code, you will see that your cube is actually a sphere. The \_\_new\_\_ method of the Cube class is being overridden. If I were to not override the method, the code inside would essentially look like this:

```
return object.__new__(cls, *args, **kwargs)
```

If you examine the two lines you will see that the only change I have made is replacing cls with the class of my choosing, Sphere. The variable cls is just the class that was passed in to the \_\_new\_\_ method to be used when creating the object. In this case it would have been Cube.

Now that we have a very basic explanation of this handy method out of the way, how can it be used?

### Factories

The best application I have found for the \_\_new\_\_ method is to be used as a factory to automatically build other classes. For example, I was writing my own wrapper for Maya Python and wanted it so when I created an instance of my main "Maya Node" wrapper class it would automatically return a sub-class depending on the type of node. If the node was a joint, it would return a JointWrapper object instead of a MayaNode object. I have since switched over to using PyMel and discovered it is doing the same thing.

Another example of this factory approach is for versioning a rig wrapper class for interacting with my rigs. This is something I did recently. I stored a version number on my rig in Maya and then had a series of wrapper classes for it: RigWrapper, RigWrapper\_2, RigWrapper\_2\_01, RigWrapper\_3, etc. Each of these rig wrapper "versions" would inherit from the previous. Inside the \_\_new\_\_ method on the original RigWrapper class I had code that would get the version number stored on the rig in the scene and then do an introspection of the file to find all other versions of the RigWrapper class. It would then do a comparison of these classes names to find the closest version without rounding up (if the rig in Maya was version 2.9 it would use RigWrapper\_2\_01 rather than RigWrapper\_3). This is the class it would then use to create and return. The rig would be correctly wrapped with the appropriate version of the wrapper class; you can call RigWrapper('ctrl\_master') and it will return an instance of RigWrapper\_2\_01.

This was powerful because it brought all the features of inheritance to my rigging interface while also being very simple to use. It allowed me to make major changes to my rigs with little concern for them breaking because of incompatibility with the tools. As long as my tools for the rigs were using the RigWrapper class it would get the correct wrapper class and work as expected, and I didn't have to do any extra work at this point in order to find which wrapper to use. All the work was already done.

### Singletons

Every once in a while you might come across an instance where you might want a class to ever be able to be created once. Nine times out of ten this probably means you should be breaking this code out to its own module, but there is still that odd time that you might have reason not to. You can use the \_\_new\_\_ method to make it so your class only ever gets created once. Here is example code for this:

```
class Singleton(object):
    _instance = None

    def __init__(self, *args, **kwargs):
        # Init will always be called, so check if it has already been initialized by whether there is already an instance stored.
        if self.__class__._instance:
            return
        else:
            # If there is no instance stored, store this instance for next time.
            self.__class__._instance = self
        # Carry on with whatever initialization you want to have happen.
        self._whatever = True

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            return object.__new__(cls, *args, **kwargs)
```

### Validation

I have done this before, but I cannot fully endorse this as it creates some strange and unexpected behaviour. It is not illegal and is supported by Python, but it just doesn't feel right. Doing a quick search about it on Stack Overflow showed shared sentiments from others. What I am talking about is doing validation checks in \_\_new\_\_ and returning None if those checks are not met.

The reason this makes for unexpected and strange behaviour is that if you are creating an instance of a class, you are expecting an instance of that class to be returned. Having it return None instead is unpredictable and weird. This is a very good reason not to do this.

You can also make an argument for this, although I do not feel it beats the argument against doing this. Imagine the scenario of creating a class that requires a file path to be created. If this class is passed a path to a file that doesn't exist, the class will be useless and will error when its functions are called. You could do a os.path.exists in the \_\_new\_\_ and if it fails return None rather than creating the class. Then before you start calling any of its functions just check to make sure the class instance is equal to something. If you are creating many instances of this class and collect them in a list, you can filter the list to remove any None objects. This would ensure any object that is successfully created with the class will be working and be associated with a file on disk.

The alternative to this would be creating a function in the class called isValid or doesFileExist, or something similar. Before calling a function that requires the file to exist, call this function just to ensure that it does. This is a lot more clear since you will have a function stating exactly what is happening, rather than you just magically getting None returned. It isn't quite as clean though since you will be having checks all over the place to make sure the file exists. It would be easier if the class just never exists if the file doesn't exist.

In the end, this validation approach is a very grey area. I'm not really all that keen on one approach over another. The jury is still out on this one for me. Not a huge fan though.

It would be great to hear if anyone out there is using \_\_new\_\_ in other ways. These are just the uses I have found for it, but I am sure there are many other great applications.
