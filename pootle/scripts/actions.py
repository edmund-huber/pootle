#!/usr/bin/env python
"""

Dynamic loading and registration for user (administrator)-provided extension
actions.

"""

import logging
import os
import pkgutil
import sys

EXTDIR = 'ext_actions'


class ExtensionAction(object):
    """User (administrator)-provided actions for execution in Pootle UI

    This is an (abstract) base class for all extension actions, creating one
    would not actually register any actions in the menu system - it exists
    just to provide a place for any common code

    """

    # Dictionary mapping ExtensionAction classes to lists of their instances
    _instances = {}

    @classmethod
    def instances(cls, rescan=False):
        """Return all instances of this class

        This will attempt to load any classes the first time it is called
        (or any time that rescan=True).

        """
        if not ExtensionAction._instances or rescan:
            dirname = os.path.sep.join([os.path.dirname(__file__), EXTDIR])

            # __import__(dirmod) is needed to suppress RuntimeWarning:
            # Parent module ... not found while handling absolute import
            dirmod = '.'.join(dirname.split(os.path.sep))
            if dirmod not in sys.modules:
                __import__(dirmod)

            for importer, package_name, _ in pkgutil.iter_modules([dirname]):
                full_package_name = '.'.join(dirname.split(os.path.sep) +
                                             [package_name])
                if full_package_name not in sys.modules:
                    try:
                        importer.find_module(package_name).load_module(
                            full_package_name)
                    except StandardError, e:
                        logging.error("bad extension action module %s: %s",
                                      package_name, repr(e))
                    else:
                        logging.info("loaded extension action module %s",
                                     full_package_name)

        if cls not in ExtensionAction._instances:
            ExtensionAction._instances[cls] = []

        return cls._instances[cls]

    def __init__(self, category, title):
        """
        >>> a = ExtensionAction('a', 'b')
        >>> assert a in a.instances()
        >>> assert a in a.instances(rescan=True)
        """
        self._category = category
        self._title = title
        for cls in type(self).__mro__:
            if cls is not object:
                if cls not in self._instances:
                    ExtensionAction._instances[cls] = [self]
                else:
                    ExtensionAction._instances[cls].append(self)
                logging.debug("instances[%s] = %s",
                              cls.__name__, ExtensionAction._instances[cls])

    def __repr__(self):
        """
        >>> print ExtensionAction('cat', 'dog')
        ExtensionAction("cat", "dog")
        >>> print ProjectAction(title="dog", category="cat")
        ProjectAction(category="cat", title="dog")
        """
        if type(self) is ExtensionAction:
            return (type(self).__name__ + '("' + self.category + '", "' +
                    self.title + '")')
        else:
            return (type(self).__name__ + '(category="' + self.category +
                    '", title="' + self.title + '")')

    @property
    def category(self):
        """Heading for action grouping

        The (unlocalized) text of the category in which the action will be
        placed.  An example might be "Translate offline" if the action would
        be placed together with the "Download (.zip)" and "Upload" actions.

        """
        return self._category

    @property
    def title(self):
        """The (unlocalized) text for the action link."""
        return self._title

    def run(self, project='*', language='*', store='*'):
        """Run an extension action: this base class implementation just logs"""
        logging.warning("%s lacks run(): %s for proj %s lang %s store %s",
                        type(self), self.title, project, language, store)

    def showoutput(self, stream):
        """Display results of action in the current page"""
        # display output on the current page

    def newpage(self, stream):
        """Display results of action on a results page"""
        # display output on a new results page

    def returnfile(self, stream):
        """Display link to a file containing results"""
        # display link to results file


class ProjectAction(ExtensionAction):
    """Project-level action

    This is an extension action that operates on a project (across all
    languages).

    """

    def __init__(self, **kwargs):
        """
        >>> print ProjectAction(category="cat", title="dog")
        ProjectAction(category="cat", title="dog")
        """
        ExtensionAction.__init__(self, kwargs['category'], kwargs['title'])
        logging.debug("%s.__init__ %s", type(self).__name__, kwargs['title'])

        # register action on project page
        # register action on language page
        # register action on translationproject page
        # register action on store page


class LanguageAction(ExtensionAction):
    """Language global action

    This is an extension action that operates on a language (across all
    projects).

    """

    def __init__(self, **kwargs):
        """
        >>> print LanguageAction(category="cat", title="dog")
        LanguageAction(category="cat", title="dog")
        """
        ExtensionAction.__init__(self, kwargs['category'], kwargs['title'])
        logging.debug("%s.__init__ %s", type(self).__name__, kwargs['title'])

        # register action on language page
        # register action on translationproject page
        # register action on store page


class TranslationProjectAction(ExtensionAction):
    """Project + Language action

    This is an extension action that operates on a particular translation of
    a project for a particular language.

    """

    def __init__(self, **kwargs):
        """
        >>> print TranslationProjectAction(category="cat", title="dog")
        TranslationProjectAction(category="cat", title="dog")
        """
        ExtensionAction.__init__(self, kwargs['category'], kwargs['title'])
        logging.debug("%s.__init__ %s", type(self).__name__, kwargs['title'])

        # register action on translationproject page
        # register action on store page


class StoreAction(ExtensionAction):
    """Individual store (file) action

    This is an extension action that operates on a particular store
    (translation file) of a particular language for a particular project.

    """

    def __init__(self, **kwargs):
        """
        >>> print StoreAction(category="cat", title="dog")
        StoreAction(category="cat", title="dog")
        """
        ExtensionAction.__init__(self, kwargs['category'], kwargs['title'])
        logging.debug("%s.__init__ %s", type(self).__name__, kwargs['title'])

        # register action on store page


class CommandAction(object):
    """Command-line action mixin

    This is a class for extension actions that can be invoked from the command
    line; it is intended to be used as a mixin for other extension actions;
    since you can always write an standalone script for a command action that
    is not available within the Pootle UI.

    """

    def __init__(self, **kwargs):
        logging.debug("%s.__init__ %s", type(self).__name__, kwargs['title'])
        # register action as management command

    def parseargs(self, *args):
        """Parse command line arguments"""
        # argparse handling?

    def runcmd(self):
        """run management command"""
        # print usage?

if __name__ == "__main__":
    import doctest
    doctest.testmod()