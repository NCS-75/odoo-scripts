#!/usr/bin/env python

import argparse
import os
import polib
from os.path import join as j


def check_po_percent(path):
    for addon in os.listdir(path):
        i18n_path = j(path, addon, 'i18n')
        if not os.path.exists(i18n_path):
            print("skip '%s'..." % i18n_path)
            continue
        print("Processing '%s'... in %s" % (addon, i18n_path))
        for lang in sorted(filter(lambda x: x.endswith('.po'), os.listdir(i18n_path))):
            language = lang.replace('.po', '')

            if len(language.split('_')) > 1 and language not in ['zh_CN', 'pt_BR', 'zh_TW']:
                # clean only main translations
                continue

            po_path = j(i18n_path, lang)
            po = polib.pofile(po_path, wrapwidth=78)
            save = False
            for entry in po:
                rfrom, rto = False, False

                if entry.msgstr and "\\n" in entry.msgstr:
                    # assert: Translation terms may not include escaped newlines
                    rfrom, rto = '\\n', '\n'

                if entry.msgstr and '%s' in entry.msgid and '%s' not in entry.msgstr:

                    if '% s' in entry.msgstr:
                        if ' %s' in entry.msgid:
                            rfrom, rto = '% s', ' %s'
                        elif '%s ' in entry.msgid:
                            rfrom, rto = '% s', '%s '
                        else:
                            rfrom, rto = '% s', '%s'
                    elif '%S' in entry.msgstr:
                        rfrom = '%S'
                    elif 'S%' in entry.msgstr:
                        rfrom = 'S%'
                    elif 's%' in entry.msgstr:
                        rfrom = 's%'
                    elif '%s' in entry.msgid and '%' in entry.msgstr:
                        rfrom = '%'
                        rto = '%s'
                    elif entry.msgid.startswith('%s'):
                        rfrom = entry.msgstr
                        rto = '%s '+rfrom
                    elif entry.msgid.endswith('%s'):
                        rfrom = entry.msgstr
                        rto = rfrom + ' %s'
                    else:
                        print(f"Bad translation in {po_path} :\n\t{entry.msgid}")

                if rfrom:
                    entry.msgstr = entry.msgstr.replace(rfrom, rto or '%s')
                    save = True

            if save:
                po.save()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--trad', required=True,
                        help='path to reference translations')

    args = parser.parse_args()
    check_po_percent(args.trad)
