# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: configuration.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13\x63onfiguration.proto\x12\x11PluginAdapter.Api\"\xc0\x01\n\rConfiguration\x12\x34\n\x05items\x18\x01 \x03(\x0b\x32%.PluginAdapter.Api.Configuration.Item\x1ay\n\x04Item\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x10\n\x06string\x18\x03 \x01(\tH\x00\x12\x11\n\x07integer\x18\x04 \x01(\x03H\x00\x12\x0f\n\x05\x66loat\x18\x05 \x01(\x02H\x00\x12\x11\n\x07\x62oolean\x18\x06 \x01(\x08H\x00\x42\x06\n\x04typeb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'configuration_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_CONFIGURATION']._serialized_start=43
  _globals['_CONFIGURATION']._serialized_end=235
  _globals['_CONFIGURATION_ITEM']._serialized_start=114
  _globals['_CONFIGURATION_ITEM']._serialized_end=235
# @@protoc_insertion_point(module_scope)
