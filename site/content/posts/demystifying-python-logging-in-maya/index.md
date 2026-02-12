+++
title = "Python logging in Maya"
date = 2021-07-13T00:00:00Z
tags = ["maya", "python"]
+++


The logging module, while something I’ve been using for years, is not something I can say I’ve been clear on. I’ve dug in more recently and thought I would share some quick learnings.

## Logger Hierarchy

The first item to note is that Python’s logging module behaves as an inheritance hierarchy. This hierarchy will automatically kick in by using dot notation in the naming of your logger. For example, _“eh.bee.sea”_ inherits from _“eh.bee”_, which inherits from _“eh”_.

That should help explain why you will see the following line in most places utilizing the logging module.

log = logging.getLogger(\_\_name\_\_)

This code will…

- Attempt to grab a logger instance, from a globally cached collection of loggers, by using the current module’s name.
- Create a new logger if it can’t find an already existing one using the name provided.
- Inherit the configuration for the new logger from any existing loggers that will be parents,
- Store this new logger instance in the global cache for future lookup.

The beauty of this code is, it’s the same no matter where you are in your codebase. It is the hierarchy magic that makes it all work.

## Make Your Own

I've found the way to get this working best is to configure your logger inside the _\_\_init\_\_.py_ of your highest level Python package. Doing this will get the logger using the package's name, leaving out _"\_\_init\_\_"._

For example, if you run `logging.getLogger(__name__)` in _my\_package/\_\_init\_\_.py_, it will create a logger by the name _“my\_package_.”

That means you can then run `log = logging.getLogger(__name__)` in any submodules or packages under _my\_package_, and it will inherit that initial configuration you made.

## Maya's Root Logger

The root logger, at the very top of the logging hierarchy, is already pre-configured with a log handler from Autodesk. This handler is what prints output to Maya's script editor and formats it how it does.

The main thing to note here is, when implementing your own logger and custom handlers, there is no need to set up output to the script editor. The root logger already handles this functionality, which you will be inheriting from.
