import datetime
import re

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from markitup.fields import MarkupField

class InfoPage(models.Model):
    """
    InfoPage - store static pages in the database so they can be edited in the admin.

    There are several pages on a site that are static - ie they don't change very often. However sometimes they need to change and it is conveniant to do this via the admin, rather than editing the html on disk.

    This module allows you to do that.

    Each page has a slug - which is used to identify it in the url. So for example if you had a site FAQ the slug might be 'faq' and its url would become something like http://example.com/info/faq - where 'info' is where these pages are stored.

    Pages also have titles - which are shown at the top of the page.

    Both slugs and titles must be unique to each page.

    The content of the page is formatted using 'markdown' - which allows you to include bulleted lists, headings, styling and links.

    The page with the slug 'index' is special - it is used as the index page to all the other info pages, and so should probably be a table of contents or similar.
    """

    created = models.DateTimeField( auto_now_add=True, default=datetime.datetime.now(), )
    updated = models.DateTimeField( auto_now=True,     default=datetime.datetime.now(), )    

    slug    = models.SlugField(unique=True)
    title   = models.CharField(max_length=255, unique=True)
    content = MarkupField( help_text="When linking to other pages use their slugs as the address (note that these links do not work in the preview, but will on the real site)")

    def __unicode__(self):
        return self.title

    def name(self):
        return str(self)

    def content_with_anchors(self):
        """ Returns content with an anchor tag <a> inserted above every heading element 
            (the anchor name is the slugified heading text). For example:
            <h2>Halt! Who goes there?"</h2>
            becomes
            <a name="halt-who-goes-there">
            <h2>Halt! Who goes there?"</h2>""" 
        def prepend_anchor_tag( match ):
            return '<a name="%s"></a>%s%s' % (slugify(match.group(2)), match.group(1), match.group(2))
        headings_regexp = re.compile( '(<h\d+[^>]*>)([^<]*)')
        return headings_regexp.sub( prepend_anchor_tag, self.content.rendered)
         
    @models.permalink
    def get_absolute_url(self):
        return ( 'info_page', [ self.slug ] )

    def get_admin_url(self):
        url = reverse(
            'admin:%s_%s_change' % ( self._meta.app_label, self._meta.module_name),
            args=[self.id]
        )
        return url
        
    class Meta:
        ordering = ['title']      
