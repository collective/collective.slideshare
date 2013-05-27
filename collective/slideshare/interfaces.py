"""Define interfaces for your add-on.
"""
from zope.interface import Interface, invariant, Invalid
from zope import schema

from zope.i18nmessageid import MessageFactory
from plone.theme.interfaces import IDefaultPloneLayer

from collective.slideshare import slideshareMessageFactory as _

from collective.slideshare import vocabularies

class MissingUserPwd(Invalid):
    __doc__ = _(u"You must provide a username and password for this to work")


class ISlideshareLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ISlideshareSettings(Interface):
    """Global settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    api_key = schema.TextLine(title=_(u"API Key"),
        description = _(u"Apply for an Key at http://www.slideshare.net/developers/applyforapi"),
        required = True,
        )

    shared_secret = schema.TextLine(title=_(u"Shared Secret"),
        description = _(u""),
        required = True,
        )

    user_policy = schema.Choice(title=_(u'Post as user policy'),
         description=_(u"Select if a user has to supply his credentials"),
         vocabulary=vocabularies.user_policy_vocabulary,
         default=u'fixed',
         required=True,
         )

    username = schema.TextLine(title=_(u"User"),
        description = _(u"Username of the user you post to slideshare as"),
        required = False,
        )

    password = schema.TextLine(title=_(u"Password"),
        description = _(u"password of the user you post to slideshare as"),
        required = False,
        )

    push_on_publish = schema.Bool(title=_(u"Post to Slideshare on publish"),
        description=_(u"For this to work the User and Password above must be filled in"),
        required=False,
        default=False,
        )


    width = schema.TextLine(
        title=_(u"Width"),
        description=_(
            u"Choose the width of the slides, "
            u"specified as an absolute value (e.g. '450px' or '15em'), "
            u"or relative (e.g. '100%') size."
        ),
        required=False)

    height = schema.TextLine(
        title=_(u"Height"),
        description=_(
            u"Choose the height of the slides, "
            u"specified as an absolute value (e.g. '450px' or '15em'), "
            u"or relative (e.g. '100%') size."
        ),
        required=False)


    @invariant
    def validateUserPwd(data):
        if data.push_on_publish:
            if not(data.username) and not(data.password):
                raise MissingUserPwd(_(u"You must provide a username and password to upload to slideshare."))


class IPostToSlideshareSchema(Interface):
    """ get username/password to post to slideshare """

    username = schema.TextLine(title=_(u"Username"),
        description = _(u"Your slideshare username"),
        required = False,
        )

    password = schema.TextLine(title=_(u"Password"),
        description = _(u"Your slideshare password"),
        required = False,
        )
