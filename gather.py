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

class PersonEncoder(json.JSONEncoder):
    def default(self, object):
        if isinstance(object, DT.Person):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)

class DataTrackerCollector:
    def __init__(self, use_cache=False):
        self.dt = DT.DataTracker()
        if use_cache:
                requests_cache.install_cache("dt_collector_cache")
        pathlib.Path("data").mkdir(parents=True, exist_ok=True)

    def serialise_person(self, person: DT.Person):
        pathlib.Path("data/people/%d" % (person.id)).mkdir(parents=True, exist_ok=True)
        with open("data/people/%d/metadata.json" % person.id, "w") as personMetadataFile:
            json.dump(person, personMetadataFile, indent=4, cls=PersonEncoder)

    def gather_people(self):
        pathlib.Path("data/people").mkdir(parents=True, exist_ok=True)
        print("Gathering people..")
        for person in self.dt.people():
            print(person)
            self.serialise_person(person)

    def gather(self):
        self.gather_people()

if __name__ == "__main__":
    collector = DataTrackerCollector(use_cache=True)
    collector.gather()
