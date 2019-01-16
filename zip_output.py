'''
    Run commands, base on Python 3.X
    Developer: lhuaizhong@gmail.com
'''

import os
import datetime
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def main():
    dt_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = 'config_backup_%s.zip' % dt_str
    zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir('./output', zipf)
    zipf.close()

if __name__ == '__main__':
    main()
