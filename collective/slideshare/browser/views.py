from zope.interface import implements, Interface
from zope.annotation import IAnnotations
from zope.component import getUtility
from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry

from collective.slideshare.config import KEY, SLIDES_MIMETYPES
from collective.slideshare.interfaces import ISlideshareSettings

class ISlideshareFileView(Interface):
    """
    slideshare view interface
    """

class SlideshareFileView(BrowserView):
    """
    Display slideshare embeded file
    """
    implements(ISlideshareFileView)

    def __init__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISlideshareSettings)
        super(SlideshareFileView, self).__init__(*args, **kwargs)


    def get_slid(self):
        """slideshare slideshowid or redirect to upload"""
        annotations = IAnnotations(self.context)
        sl_id = annotations.get(KEY, None)
        if sl_id:
            return sl_id
        else:
            if self.context.getContentType() in SLIDES_MIMETYPES:
                self.request.response.redirect(
                    self.context.absolute_url() + '/@@slideshare_post.html')
            else:
                msg = _(u"This file does not seem to be a presentation")
                IStatusMessage(self.request).addStatusMessage(msg, type='error')

    def get_height(self):
        return self.settings.height

    def get_width(self):
        return self.settings.width
