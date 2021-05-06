from operator import itemgetter
import platform
import re

import json
import pytest


def normalize_path(path):
    """
    Normalize absolute path to a file in a package down to a package path.
    Not foolproof, but good enough for the tests.
    """
    return re.sub(r"^.*site-packages/", "", path)

def normalize_git(git):
    git.pop('repository')
    git.pop('branch')
    git.pop('commit')
    status = git.pop('status')
    assert isinstance(status, list)
    tag = git.pop('tag', None)
    if tag:
        assert isinstance(tag, str)
    commits_since_tag = git.pop('commits_since_tag', None)
    if commits_since_tag:
        assert isinstance(commits_since_tag, int)
    git.pop('annotated_tag', None)

    commits_since_annotated_tag = git.pop(
        'commits_since_annotated_tag', None
    )
    if commits_since_annotated_tag:
        assert isinstance(commits_since_annotated_tag, int)

def normalize_metadata(metadata):
    engine = metadata['language'].pop('engine')
    assert engine == platform.python_implementation()
    version = metadata['language'].pop('version')
    assert version == platform.python_version()

    if 'frameworks' in metadata:
        frameworks = metadata['frameworks']
        for f in frameworks:
            if f['name'] == 'pytest':
                v = f.pop('version')
                assert v == pytest.__version__

def normalize_headers(dct):
    """Remove some headers which are variable between implementations.
    This allows sharing tests between web frameworks, for example.
    """
    for hdr in ['User-Agent', 'Content-Length', 'ETag', 'Cookie', 'Host']:
        value = dct.pop(hdr, None)
        assert value is None or isinstance(value, str)

def normalize_appmap(generated_appmap):
    """
    Normalize the data in generated_appmap, removing any
    environment-specific values.

    Note that attempts to access required keys will raise
    KeyError, causing the test to fail.
    """

    def normalize(dct):
        if 'classMap' in dct:
            dct['classMap'].sort(key=itemgetter('name'))
        if 'children' in dct:
            dct['children'].sort(key=itemgetter('name'))
        if 'elapsed' in dct:
            elapsed = dct.pop('elapsed')
            assert isinstance(elapsed, float)
        if 'git' in dct:
            normalize_git(dct.pop('git'))
        if 'headers' in dct:
            normalize_headers(dct['headers'])
            if len(dct['headers']) == 0:
                del dct['headers']
        if 'http_server_request' in dct:
            normalize(dct['http_server_request'])
        if 'location' in dct:
            dct['location'] = normalize_path(dct['location'])
        if 'normalized_path_info' in dct:
            del dct['normalized_path_info']
        if 'path' in dct:
            dct['path'] = normalize_path(dct['path'])
        if 'metadata' in dct:
            normalize_metadata(dct['metadata'])
        if 'object_id' in dct:
            object_id = dct.pop('object_id')
            assert isinstance(object_id, int)
        if 'value' in dct:
            # This maps all object references to the same
            # location. We don't actually need to verify that the
            # locations are correct -- if they weren't, the
            # instrumented code would be broken, right?
            v = dct['value']
            dct['value'] = re.sub(r'<(.*)( object)* at 0x.*>',
                                  r'<\1 at 0xabcdef>',
                                  v)
        return dct

    return json.loads(generated_appmap, object_hook=normalize)
