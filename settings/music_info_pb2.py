# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: music_info.proto

import sys

_b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
    name='music_info.proto',
    package='music_info',
    syntax='proto2',
    serialized_options=None,
    serialized_pb=_b(
        '\n\x10music_info.proto\x12\nmusic_info\"\xc0\x01\n\x0fVanillaStreamPB\x12\x10\n\x08\x66ilepath\x18\x01 \x01(\t\x12\x38\n\x05parts\x18\x02 \x03(\x0b\x32).music_info.VanillaStreamPB.VanillaPartPB\x1a\x61\n\rVanillaPartPB\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x0f\n\x07offsets\x18\x02 \x03(\x02\x12\x0f\n\x07lengths\x18\x03 \x03(\x02\x12\x0f\n\x07pitches\x18\x04 \x03(\x05\x12\x0f\n\x07volumes\x18\x05 \x03(\x05\"\xea\x02\n\x0cPieceOfMusic\x12\x10\n\x08\x66ilepath\x18\x01 \x02(\t\x12\r\n\x05valid\x18\x02 \x02(\x08\x12\x15\n\rmin_metronome\x18\x04 \x01(\x05\x12\x15\n\rmax_metronome\x18\x05 \x01(\x05\x12\x0b\n\x03key\x18\x06 \x01(\t\x12\x17\n\x0fkey_correlation\x18\x07 \x01(\x02\x12,\n\x05parts\x18\x08 \x03(\x0b\x32\x1d.music_info.PieceOfMusic.Part\x12$\n\x05\x65rror\x18\x0c \x01(\x0e\x32\x15.music_info.ErrorEnum\x1a\x90\x01\n\x04Part\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x15\n\raverage_pitch\x18\x02 \x01(\x02\x12\x16\n\x0e\x61verage_volume\x18\x03 \x01(\x02\x12\x17\n\x0fkey_correlation\x18\x05 \x01(\x02\x12\x17\n\x0fnote_percentage\x18\x06 \x01(\x02\x12\x19\n\x11lyrics_percentage\x18\x07 \x01(\x02\"\xbc\x01\n\x08Settings\x12\x11\n\tmin_pitch\x18\x01 \x02(\x02\x12\x11\n\tmax_pitch\x18\x02 \x02(\x02\x12\x1d\n\x15\x64\x65lete_part_threshold\x18\x03 \x02(\x02\x12\x1f\n\x17\x64\x65lete_stream_threshold\x18\x04 \x02(\x02\x12\x14\n\x0c\x61\x63\x63\x65pted_key\x18\x05 \x02(\t\x12\x0f\n\x07max_bpm\x18\x06 \x02(\x05\x12\x0f\n\x07min_bpm\x18\x07 \x02(\x05\x12\x12\n\nvalid_time\x18\x08 \x02(\t\"r\n\tMusicList\x12&\n\x08settings\x18\x01 \x02(\x0b\x32\x14.music_info.Settings\x12,\n\nmusic_data\x18\x02 \x03(\x0b\x32\x18.music_info.PieceOfMusic\x12\x0f\n\x07\x63ounter\x18\x03 \x02(\x05*{\n\tErrorEnum\x12\x18\n\x14WRONG_TIME_SIGNATURE\x10\x00\x12\r\n\tWRONG_BPM\x10\x01\x12\r\n\tWRONG_KEY\x10\x02\x12\x0f\n\x0bINVALID_KEY\x10\x03\x12\x17\n\x13LOW_CORRELATION_KEY\x10\x04\x12\x0c\n\x08NO_PARTS\x10\x05')
)

_ERRORENUM = _descriptor.EnumDescriptor(
    name='ErrorEnum',
    full_name='music_info.ErrorEnum',
    filename=None,
    file=DESCRIPTOR,
    values=[
        _descriptor.EnumValueDescriptor(
            name='WRONG_TIME_SIGNATURE', index=0, number=0,
            serialized_options=None,
            type=None),
        _descriptor.EnumValueDescriptor(
            name='WRONG_BPM', index=1, number=1,
            serialized_options=None,
            type=None),
        _descriptor.EnumValueDescriptor(
            name='WRONG_KEY', index=2, number=2,
            serialized_options=None,
            type=None),
        _descriptor.EnumValueDescriptor(
            name='INVALID_KEY', index=3, number=3,
            serialized_options=None,
            type=None),
        _descriptor.EnumValueDescriptor(
            name='LOW_CORRELATION_KEY', index=4, number=4,
            serialized_options=None,
            type=None),
        _descriptor.EnumValueDescriptor(
            name='NO_PARTS', index=5, number=5,
            serialized_options=None,
            type=None),
    ],
    containing_type=None,
    serialized_options=None,
    serialized_start=899,
    serialized_end=1022,
)
_sym_db.RegisterEnumDescriptor(_ERRORENUM)

ErrorEnum = enum_type_wrapper.EnumTypeWrapper(_ERRORENUM)
WRONG_TIME_SIGNATURE = 0
WRONG_BPM = 1
WRONG_KEY = 2
INVALID_KEY = 3
LOW_CORRELATION_KEY = 4
NO_PARTS = 5

_VANILLASTREAMPB_VANILLAPARTPB = _descriptor.Descriptor(
    name='VanillaPartPB',
    full_name='music_info.VanillaStreamPB.VanillaPartPB',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='name', full_name='music_info.VanillaStreamPB.VanillaPartPB.name', index=0,
            number=1, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='offsets', full_name='music_info.VanillaStreamPB.VanillaPartPB.offsets', index=1,
            number=2, type=2, cpp_type=6, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='lengths', full_name='music_info.VanillaStreamPB.VanillaPartPB.lengths', index=2,
            number=3, type=2, cpp_type=6, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='pitches', full_name='music_info.VanillaStreamPB.VanillaPartPB.pitches', index=3,
            number=4, type=5, cpp_type=1, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='volumes', full_name='music_info.VanillaStreamPB.VanillaPartPB.volumes', index=4,
            number=5, type=5, cpp_type=1, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=128,
    serialized_end=225,
)

_VANILLASTREAMPB = _descriptor.Descriptor(
    name='VanillaStreamPB',
    full_name='music_info.VanillaStreamPB',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='filepath', full_name='music_info.VanillaStreamPB.filepath', index=0,
            number=1, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='parts', full_name='music_info.VanillaStreamPB.parts', index=1,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[_VANILLASTREAMPB_VANILLAPARTPB, ],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=33,
    serialized_end=225,
)


_PIECEOFMUSIC_PART = _descriptor.Descriptor(
    name='Part',
    full_name='music_info.PieceOfMusic.Part',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='name', full_name='music_info.PieceOfMusic.Part.name', index=0,
            number=1, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='average_pitch', full_name='music_info.PieceOfMusic.Part.average_pitch', index=1,
            number=2, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='average_volume', full_name='music_info.PieceOfMusic.Part.average_volume', index=2,
            number=3, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='key_correlation', full_name='music_info.PieceOfMusic.Part.key_correlation', index=3,
            number=5, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='note_percentage', full_name='music_info.PieceOfMusic.Part.note_percentage', index=4,
            number=6, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='lyrics_percentage', full_name='music_info.PieceOfMusic.Part.lyrics_percentage', index=5,
            number=7, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=446,
    serialized_end=590,
)

_PIECEOFMUSIC = _descriptor.Descriptor(
    name='PieceOfMusic',
    full_name='music_info.PieceOfMusic',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='filepath', full_name='music_info.PieceOfMusic.filepath', index=0,
            number=1, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='valid', full_name='music_info.PieceOfMusic.valid', index=1,
            number=2, type=8, cpp_type=7, label=2,
            has_default_value=False, default_value=False,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='min_metronome', full_name='music_info.PieceOfMusic.min_metronome', index=2,
            number=4, type=5, cpp_type=1, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='max_metronome', full_name='music_info.PieceOfMusic.max_metronome', index=3,
            number=5, type=5, cpp_type=1, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='key', full_name='music_info.PieceOfMusic.key', index=4,
            number=6, type=9, cpp_type=9, label=1,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='key_correlation', full_name='music_info.PieceOfMusic.key_correlation', index=5,
            number=7, type=2, cpp_type=6, label=1,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='parts', full_name='music_info.PieceOfMusic.parts', index=6,
            number=8, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='error', full_name='music_info.PieceOfMusic.error', index=7,
            number=12, type=14, cpp_type=8, label=1,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[_PIECEOFMUSIC_PART, ],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=228,
    serialized_end=590,
)


_SETTINGS = _descriptor.Descriptor(
    name='Settings',
    full_name='music_info.Settings',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='min_pitch', full_name='music_info.Settings.min_pitch', index=0,
            number=1, type=2, cpp_type=6, label=2,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='max_pitch', full_name='music_info.Settings.max_pitch', index=1,
            number=2, type=2, cpp_type=6, label=2,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='delete_part_threshold', full_name='music_info.Settings.delete_part_threshold', index=2,
            number=3, type=2, cpp_type=6, label=2,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='delete_stream_threshold', full_name='music_info.Settings.delete_stream_threshold', index=3,
            number=4, type=2, cpp_type=6, label=2,
            has_default_value=False, default_value=float(0),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='accepted_key', full_name='music_info.Settings.accepted_key', index=4,
            number=5, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='max_bpm', full_name='music_info.Settings.max_bpm', index=5,
            number=6, type=5, cpp_type=1, label=2,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='min_bpm', full_name='music_info.Settings.min_bpm', index=6,
            number=7, type=5, cpp_type=1, label=2,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='valid_time', full_name='music_info.Settings.valid_time', index=7,
            number=8, type=9, cpp_type=9, label=2,
            has_default_value=False, default_value=_b("").decode('utf-8'),
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=593,
    serialized_end=781,
)


_MUSICLIST = _descriptor.Descriptor(
    name='MusicList',
    full_name='music_info.MusicList',
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    fields=[
        _descriptor.FieldDescriptor(
            name='settings', full_name='music_info.MusicList.settings', index=0,
            number=1, type=11, cpp_type=10, label=2,
            has_default_value=False, default_value=None,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='music_data', full_name='music_info.MusicList.music_data', index=1,
            number=2, type=11, cpp_type=10, label=3,
            has_default_value=False, default_value=[],
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
        _descriptor.FieldDescriptor(
            name='counter', full_name='music_info.MusicList.counter', index=2,
            number=3, type=5, cpp_type=1, label=2,
            has_default_value=False, default_value=0,
            message_type=None, enum_type=None, containing_type=None,
            is_extension=False, extension_scope=None,
            serialized_options=None, file=DESCRIPTOR),
    ],
    extensions=[
    ],
    nested_types=[],
    enum_types=[
    ],
    serialized_options=None,
    is_extendable=False,
    syntax='proto2',
    extension_ranges=[],
    oneofs=[
    ],
    serialized_start=783,
    serialized_end=897,
)

_VANILLASTREAMPB_VANILLAPARTPB.containing_type = _VANILLASTREAMPB
_VANILLASTREAMPB.fields_by_name['parts'].message_type = _VANILLASTREAMPB_VANILLAPARTPB
_PIECEOFMUSIC_PART.containing_type = _PIECEOFMUSIC
_PIECEOFMUSIC.fields_by_name['parts'].message_type = _PIECEOFMUSIC_PART
_PIECEOFMUSIC.fields_by_name['error'].enum_type = _ERRORENUM
_MUSICLIST.fields_by_name['settings'].message_type = _SETTINGS
_MUSICLIST.fields_by_name['music_data'].message_type = _PIECEOFMUSIC
DESCRIPTOR.message_types_by_name['VanillaStreamPB'] = _VANILLASTREAMPB
DESCRIPTOR.message_types_by_name['PieceOfMusic'] = _PIECEOFMUSIC
DESCRIPTOR.message_types_by_name['Settings'] = _SETTINGS
DESCRIPTOR.message_types_by_name['MusicList'] = _MUSICLIST
DESCRIPTOR.enum_types_by_name['ErrorEnum'] = _ERRORENUM
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

VanillaStreamPB = _reflection.GeneratedProtocolMessageType('VanillaStreamPB', (_message.Message,), dict(

    VanillaPartPB=_reflection.GeneratedProtocolMessageType('VanillaPartPB', (_message.Message,), dict(
        DESCRIPTOR=_VANILLASTREAMPB_VANILLAPARTPB,
        __module__='music_info_pb2'
        # @@protoc_insertion_point(class_scope:music_info.VanillaStreamPB.VanillaPartPB)
    ))
    ,
    DESCRIPTOR=_VANILLASTREAMPB,
    __module__='music_info_pb2'
    # @@protoc_insertion_point(class_scope:music_info.VanillaStreamPB)
))
_sym_db.RegisterMessage(VanillaStreamPB)
_sym_db.RegisterMessage(VanillaStreamPB.VanillaPartPB)

PieceOfMusic = _reflection.GeneratedProtocolMessageType('PieceOfMusic', (_message.Message,), dict(

    Part=_reflection.GeneratedProtocolMessageType('Part', (_message.Message,), dict(
        DESCRIPTOR=_PIECEOFMUSIC_PART,
        __module__='music_info_pb2'
        # @@protoc_insertion_point(class_scope:music_info.PieceOfMusic.Part)
    ))
    ,
    DESCRIPTOR=_PIECEOFMUSIC,
    __module__='music_info_pb2'
    # @@protoc_insertion_point(class_scope:music_info.PieceOfMusic)
))
_sym_db.RegisterMessage(PieceOfMusic)
_sym_db.RegisterMessage(PieceOfMusic.Part)

Settings = _reflection.GeneratedProtocolMessageType('Settings', (_message.Message,), dict(
    DESCRIPTOR=_SETTINGS,
    __module__='music_info_pb2'
    # @@protoc_insertion_point(class_scope:music_info.Settings)
))
_sym_db.RegisterMessage(Settings)

MusicList = _reflection.GeneratedProtocolMessageType('MusicList', (_message.Message,), dict(
    DESCRIPTOR=_MUSICLIST,
    __module__='music_info_pb2'
    # @@protoc_insertion_point(class_scope:music_info.MusicList)
))
_sym_db.RegisterMessage(MusicList)

# @@protoc_insertion_point(module_scope)
