from xml.etree.cElementTree import *
from xml.etree.ElementTree import XML as XML
from xml.etree.ElementTree import Element as _Element
from xml.etree.ElementTree import *

from _typeshed import Incomplete
from lxml.etree import *

class Element(_Element):
    attrib: Incomplete
    def __init__(self, tag, attrib=..., **extra) -> None: ...

def SubElement(parent, tag, attrib=..., **extra): ...

class ElementTree(_ElementTree):
    def write(
        self,
        file_or_filename,
        encoding: Incomplete | None = ...,
        xml_declaration: bool = ...,
        method: Incomplete | None = ...,
        doctype: Incomplete | None = ...,
        pretty_print: bool = ...,
    ) -> None: ...

def tostring(
    element,
    encoding: Incomplete | None = ...,
    xml_declaration: Incomplete | None = ...,
    method: Incomplete | None = ...,
    doctype: Incomplete | None = ...,
    pretty_print: bool = ...,
): ...

# Names in __all__ with no definition:
#   Comment
#   PI
#   ParseError
#   ProcessingInstruction
#   QName
#   TreeBuilder
#   XMLParser
#   dump
#   fromstring
#   fromstringlist
#   iselement
#   iterparse
#   parse
#   register_namespace
#   tostringlist
