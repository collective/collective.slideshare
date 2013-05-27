import logging
from cStringIO import StringIO

from zope import interface, schema
from zope.formlib import form
from zope.formlib.textwidgets import PasswordWidget
from zope.component import getUtility
from zope.annotation import IAnnotations

from five.formlib import formbase

from plone.registry.interfaces import IRegistry
from Products.statusmessages.interfaces import IStatusMessage

import slideshare

from collective.slideshare import slideshareMessageFactory as _
from collective.slideshare.interfaces import IPostToSlideshareSchema, ISlideshareSettings
from collective.slideshare import KEY

logger = logging.getLogger('collective.slideshare')

class PostToSlideshare(formbase.PageForm):
    form_fields = form.FormFields(IPostToSlideshareSchema)
    form_fields['password'].custom_widget = PasswordWidget
    label = _(u'Post to Slideshare')
    description = _(u'Supply your Slideshare credentials to upload')

    def __init__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISlideshareSettings)
        if self.settings.user_policy == "fixed":
            self.description = ""
            self.form_fields = self.form_fields.omit('username', 'password')
        elif self.settings.user_policy == "user":
            un = self.form_fields.get('username')
            un.field.required = True
            pw = self.form_fields.get('password')
            pw.field.required = True
        elif self.settings.user_policy == "optional":
            self.description = _(u"""Supply your Slideshare credentials
            if you want to upload the presentation to your own account.
            Your credentials will not be stored""")
            un = self.form_fields.get('username')
            un.field.required = False
            pw = self.form_fields.get('password')
            pw.field.required = False
        super(PostToSlideshare, self).__init__(*args, **kwargs)



    @property
    def next_url(self):
        url = self.context.absolute_url()
        url += '/view'
        return url


    @form.action('Submit')
    def actionSubmit(self, action, data):
        url = self.context.absolute_url()
        if self.settings.api_key and self.settings.shared_secret:
            api = slideshare.SlideshareAPI(self.settings.api_key,
                self.settings.shared_secret)
        else:
            msg = _(u"Slideshare API_KEY or SHARED_SECRET missing")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            self.request.response.redirect(self.next_url)
            return
        if self.settings.user_policy == "fixed":
            username = self.settings.username
            password = self.settings.password
        elif self.settings.user_policy == "user":
            username = data.get('username')
            password = data.get('password')
        elif self.settings.user_policy == "optional":
            username = data.get('username')
            password = data.get('password')
            if not(username and password):
                username = self.settings.username
                password = self.settings.password
        else:
            username = None
            password = None
        if not(username and password):
            msg = _(u"Slideshare USERNAME or PASSWORD missing")
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return
        srcfile = dict(
            filehandle=self.context.getFile().getIterator(),
            filename=self.context.getFilename(),
            mimetype=self.context.getContentType()
            )
        sls = api.upload_slideshow(username, password,
                slideshow_title = self.context.Title(),
                slideshow_srcfile = srcfile,
                slideshow_description = self.context.Description(),
                slideshow_tags = ','.join(self.context.Subject()))
        sl_id = sls['SlideShowUploaded']['SlideShowID']
        annotations = IAnnotations(self.context)
        annotations[KEY] = sl_id
        self.request.response.redirect(self.next_url)
        msg = _(u"Slideshow uploaded")
        IStatusMessage(self.request).addStatusMessage(msg, type='error')


    @form.action('Cancel')
    def actionCancel(self, action, data):
        annotations = IAnnotations(self.context)
        self.request.response.redirect(self.next_url)
