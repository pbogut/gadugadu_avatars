#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Show Gadu Gadu Avatars in Gajim

:author: Paweł (Smeagol) Bogut <pbogut@smeagol.pl>
:since: 30 July 2008
:copyright: Copyright (2013) Paweł (Smeagol) Bogut <pbogut@smeagol.pl>
:license: GPL
'''

import gtk
import base64
import urllib2
from common import gajim
from common import helpers
from common import ged
from plugins import GajimPlugin
from plugins.helpers import log, log_calls
from plugins.gui import GajimPluginConfigDialog

class GaduGaduAvatarsPlugin(GajimPlugin):

    @log_calls('GaduGaduAvatarsPlugin')
    def init(self):
        self.description = _('''Show Gadu Gadu Avatars in Gajim.''')

        self.config_dialog = GaduGaduAvatarsPluginConfigDialog(self)

        self.config_default_values = {
            'gadugadu_transport_domain': ('gg.uaznia.net', 'Transport domain used for GaduGadu support'),
        }

        self.events_handlers = {
            'roster-info': (ged.GUI2, self.on_roster_info)
        }

    @log_calls('GaduGaduAvatarsPlugin')
    def on_roster_info(self, object):
        domain = self.config['gadugadu_transport_domain']
        if object.jid.find(domain) > 1:
            url = 'http://avatars.gg.pl/user,'+object.jid.replace("@"+domain, '')+'/s,160x160'
            response = urllib2.urlopen(url)
            loader = gtk.gdk.PixbufLoader()
            binary = response.read()
            response.close()
            if binary:
                loader.write(binary)
                loader.close()
                pixbuf = loader.get_pixbuf()
                gajim.interface.save_avatar_files(object.jid, pixbuf, local=True)
            else:
                #no picture found so we close loader with tiniest i could find to avoid errors
                loader.write(base64.b64decode('R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='))
                loader.close()
                #iam deleting current avatar, not sure if i should, should i?
                #gajim.interface.remove_avatar_files(object.jid, local=True)

class GaduGaduAvatarsPluginConfigDialog(GajimPluginConfigDialog):

    def init(self):
        self.GTK_BUILDER_FILE_PATH = self.plugin.local_file_path('config_dialog.ui')
        self.xml = gtk.Builder()
        self.xml.set_translation_domain('gajim_plugins')
        self.xml.add_objects_from_file(self.GTK_BUILDER_FILE_PATH,
                                 ['gadugadu_avatars_config_vbox'])
        self.config_vbox = self.xml.get_object('gadugadu_avatars_config_vbox')
        self.child.pack_start(self.config_vbox)
        self.xml.connect_signals(self)
        self.connect('hide', self.on_hide)

    def on_run(self):
        widget = self.xml.get_object('gadugadu_transport_domain')
        widget.set_text(str(self.plugin.config['gadugadu_transport_domain']))

    def on_hide(self, widget):
        widget = self.xml.get_object('gadugadu_transport_domain')
        self.plugin.config['gadugadu_transport_domain'] = widget.get_text()
