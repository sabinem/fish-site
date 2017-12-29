#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import hashlib
import json
import requests
import sys

# Extract certain fields from the releases, given on stdin.
# Add some keys to make jekyll's life easier.
# Output the result to stdout.

def format_size(bytecount):
  """ Format a byte count in megabytes """
  return '%.1f MB' % (int(bytecount) / (1024 * 1024))

def sha1of(url):
  """ return the sha1 of the contents of the URL """
  sys.stderr.write("sha1 of %s...\n" % url)
  data = requests.get(url).content
  result = hashlib.sha1(data).hexdigest()
  sys.stderr.write("Got %s\n" % result)
  return result

def get_asset(release, extension):
  """ return the asset dictionary for the asset with the given extension """
  vals = [asset for asset in release['assets']
          if asset['name'].endswith(extension)]
  if len(vals) > 1:
    sys.stderr.write('Warning: Multiple %s found for release %s'
                     % (extension, release['tag_name']))
  return vals[0] if vals else {}

releases = json.load(sys.stdin, object_pairs_hook=OrderedDict)
for rel in releases:
  name = rel['tag_name']
  tarball = get_asset(rel, '.tar.gz')
  # Skip old releases without tarballs
  if not tarball:
    continue
  macpkg = get_asset(rel, '.pkg')
  macapp = get_asset(rel, '.app.zip')
  rel.update({
    'md_tarball_name':tarball['name'],
    'md_tarball_url':tarball['browser_download_url'],
    'md_tarball_size':format_size(tarball['size']),
    'md_mac_app_url':macapp.get('browser_download_url', ''),
    'md_mac_pkg_url':macpkg.get('browser_download_url', ''),
  })
  # Compute the SHA1 for the first tarball only.
  if rel is releases[0]:
    rel['md_tarball_sha1'] = sha1of(tarball['browser_download_url'])

# We've modified the dictionaries in place, output them again.
json.dump(releases, sys.stdout, indent=4)
