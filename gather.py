# Copyright (C) 2020 University of Glasgow
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import ietfdata.datatracker as DT
import requests_cache
import pathlib
import json
import requests
import datetime
import os
import shutil
import dateutil
import pytz

from typing import Iterator, Optional

class EncodeUsingToJSON(json.JSONEncoder):
    def default(self, object):
        return object.toJSON()


class SerialisablePersonEvent:
    type         : str
    desc         : str
    time         : str

    def __init__(self, event: DT.PersonEvent):
        self.type = event.type
        self.desc = event.desc
        self.time = event.time

    def toJSON(self):
        return self.__dict__

     
class SerialisablePersonAlias:
    name         : str

    def __init__(self, alias: DT.PersonAlias):
        self.name = alias.name

    def toJSON(self):
        return self.__dict__


class SerialisableEmail:
    address      : str
    time         : str
    origin       : str
    primary      : bool
    active       : bool

    def __init__(self, email: DT.Email):
        self.address = email.address
        self.time = email.time
        self.origin = email.origin
        self.primary = email.primary
        self.active = email.active

    def toJSON(self):
        return self.__dict__


class SerialisablePerson:
    id              : int
    name            : str
    name_from_draft : str
    ascii           : str
    ascii_short     : Optional[str]
    user            : str
    time            : str
    photo           : str
    photo_thumb     : str
    biography       : str
    consent         : bool

    def __init__(self, person: DT.Person, emails: Iterator[DT.Email], aliases: Iterator[DT.PersonAlias], events: Iterator[DT.PersonEvent]):
        self.id = person.id
        self.name = person.name
        self.name_from_draft = person.name_from_draft
        self.ascii = person.ascii
        self.ascii_short = person.ascii_short
        self.user = person.user
        self.time = person.time
        self.photo = person.photo
        self.photo_thumb = person.photo_thumb
        self.biography = person.biography
        self.consent = person.consent
        self.emails = [SerialisableEmail(email) for email in emails]
        self.aliases = [SerialisablePersonAlias(alias) for alias in aliases]
        self.events = [SerialisablePersonEvent(event) for event in events]

    def toJSON(self):
        return self.__dict__


class DataTrackerCollector:
    def __init__(self, use_cache=False):
        self.dt = DT.DataTracker()
        if use_cache:
                requests_cache.install_cache("dt_collector_cache")
        pathlib.Path("data").mkdir(parents=True, exist_ok=True)

    def get_file_if_changed(self, uri: str, dest_filename: str):
        r = requests.head(uri)
        remote_lastmodified = dateutil.parser.parse(r.headers['last-modified'])
        try:
            local_lastmodified = pytz.UTC.localize(datetime.datetime.fromtimestamp(os.path.getmtime(dest_filename)))
        except:
            local_lastmodified = None
        if local_lastmodified is None or remote_lastmodified > local_lastmodified:
            r = requests.get(uri, verify=True)
            if r.status_code == 200:
                with open(dest_filename, "wb") as dest_file:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, dest_file)

    def serialise_person(self, person: DT.Person, emails: Iterator[DT.Email], aliases: Iterator[DT.PersonAlias], events: Iterator[DT.PersonEvent]):
        pathlib.Path("data/people/%d" % (person.id)).mkdir(parents=True, exist_ok=True)
        with open("data/people/%d/metadata.json" % person.id, "w") as personMetadataFile:
            json.dump(SerialisablePerson(person, emails, aliases, events), personMetadataFile, indent=4, cls=EncodeUsingToJSON)
        if (person.photo != "None"):
            pathlib.Path("data/people/%d/media/photo" % (person.id)).mkdir(parents=True, exist_ok=True)
            self.get_file_if_changed(person.photo, "data/people/%d/media/photo/%s" % (person.id, person.photo.split('/')[-1]))
        if (person.photo_thumb != "None"):
            pathlib.Path("data/people/%d/media/photo" % (person.id)).mkdir(parents=True, exist_ok=True)
            self.get_file_if_changed(person.photo_thumb, "data/people/%d/media/photo/%s" % (person.id, person.photo_thumb.split('/')[-1]))

    def gather_people(self):
        pathlib.Path("data/people").mkdir(parents=True, exist_ok=True)
        print("Gathering people..")
        for person in self.dt.people():
            print("Gathering data for %d.." % person.id)
            emails = self.dt.email_for_person(person)
            aliases = self.dt.person_aliases(person)
            events = self.dt.person_events(person)
            self.serialise_person(person, emails, aliases, events)

    def gather(self):
        self.gather_people()

if __name__ == "__main__":
    collector = DataTrackerCollector(use_cache=True)
    collector.gather()
