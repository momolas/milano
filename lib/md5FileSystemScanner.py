import os
from resultsWriter import Results
from resultsWriter import PotentialFile
import ntpath
from time import sleep

class Md5FileSystemScanner(object):
    def __init__(self, md5Generator, fileSystemListGeneratorProvider, iocReader, logger):
        self.md5Generator = md5Generator
        self.fileSystemListGeneratorProvider = fileSystemListGeneratorProvider
        self.iocReader = iocReader
        self.logger = logger

        self.suspect_files = iocReader.get_suspect_filenames()


    def scan_file_system(self):
        results = Results()

        should_deep_scan = (raw_input('Quick scan or deep scan (NOTE: quick scan is fast but incomprehensive)? [Q/d] ').lower() == 'd')

        results.scan_type = 'deep' if should_deep_scan == True else 'quick'
        
        self.fileSystemListGeneratorProvider.prompt_for_paths_to_scan()

        self.logger.info('')
        self.logger.info('Commencing scan...\n')
        sleep(2)

        results.start()

        pathGenerator = self.fileSystemListGeneratorProvider.get_generator()
        for path in pathGenerator:
            try:
                if self.should_scan_file(path, should_deep_scan):
                    my_md5 = self.md5Generator.compute_md5(path)
                    self.logger.info('Checking path: ' + path)
                    if self.iocReader.has_md5(my_md5):
                        self.logger.info('   Detected potentially malicious file at path: ' + path)
                        potential_category = self.iocReader.get_potential_category(my_md5)
                        results.detected_file_paths.append(PotentialFile(path, potential_category))
                    else:
                        self.logger.info('   File clean')

            except IOError, err:
                # Socket error possibly
                #print err
                # TODO - log these errors.
                pass
            except OSError, err:
                # File doesn't exist
                #print err
                # TODO - log these errors.
                pass

        results.finish()
        return results


    def should_scan_file(self, path, should_deep_scan):
        if path.startswith('/proc/') or path.startswith('/run/'):
            return False

        if should_deep_scan:
            return True
        else:
            if (os.path.getsize(path) > (500 * 1024 * 1024)):
                return False

            filename = ntpath.basename(path).lower()
            return filename in self.suspect_files


if __name__ == '__main__':
    fileSystemScanner = MD5FileSystemScanner()
    fileSystemScanner.scan_file_system()
