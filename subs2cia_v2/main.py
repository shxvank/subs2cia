from subs2cia_v2.argparser import get_args
from subs2cia_v2.sources import AVSFile, group_files
from subs2cia_v2.condense import SubCondensed

from pathlib import Path
import logging
from pprint import pprint

presets = [
    {  # preset 0
        'preset_description': "Padded and merged Japanese condensed audio",
        'threshold': 1500,
        'padding': 200,
        'partition_size': 1800,  # 30 minutes, for long movies
        'target-lang': 'ja',
    },
    {  # preset 1
        'preset_description': "Unpadded Japanese condensed audio",
        'threshold': 0,  # note: default is 0
        'padding': 0,  # note: default is 0
        'partition': 1800,  # 30 minutes, for long movies
        'target-lang': 'ja',
    },
]


def list_presets():
    for idx, preset in enumerate(presets):
        print(f"Preset {idx}")
        pprint(preset)


def start():
    args = get_args()
    args = vars(args)


    if args['verbose']:
        if args['debug']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
    elif args['debug']:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Start arguments: {args}")

    if args['list_presets']:
        list_presets()
        return

    if args['preset'] is not None:
        if abs(args['preset']) >= len(presets):
            logging.critical(f"Preset {args['preset']} does not exist")
            exit(0)
        logging.info(f"using preset {args['preset']}")
        for key, val in presets[args['preset']].items():
            if key in args.keys() and ((args[key] == False) or (args[key] ==  None)):  # override presets
                args[key] = val

    SubC_args = {key: args[key] for key in
                 ['outdir', 'condensed_video', 'padding', 'threshold', 'partition', 'split',
                  'demux_overwrite_existing', 'overwrite_existing_generated', 'keep_temporaries',
                  'target_lang', 'out_audioext']}

    if args['infiles'] is None:
        logging.info("No input files given, nothing to do.")
        exit(0)

    sources = [AVSFile(Path(file).absolute()) for file in args['infiles']]

    for s in sources:
        s.probe()
        s.get_type()

    groups = list(group_files(sources))

    condensed_files = [SubCondensed(g, **SubC_args) for g in groups]
    for c in condensed_files:
        c.get_and_partition_streams()
        c.initialize_pickers()
        c.choose_streams()
        c.process_subtitles()
        c.export()
        c.cleanup()


if __name__ == '__main__':
    start()
