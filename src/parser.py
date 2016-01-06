'''
Created on Jan 5, 2016

@author: romanr
'''
import os
import sys
import getopt
import shutil
import uuid

from bs4 import BeautifulSoup

class Parser(object):
    '''
    classdocs
    '''
    
    report = ''
    temp_dir = 'temp'

    def ReadFile(self):
        content = ''
        try:
            file = open(self.report, 'r')
            content = file.read()
        except FileNotFoundError:
            print ('Report file ', self.report, 'is missing!')
        finally:
            file.close()
            
        return content


    def WriteFile(self, content):
        report_dir, report_name = os.path.split(self.report)
        new_file_dir = os.path.join(report_dir, self.temp_dir)
        
        if not os.path.isdir(new_file_dir):
            os.makedirs(new_file_dir)
            
        new_file_path = os.path.join(new_file_dir, report_name)
        try:
            file = open(new_file_path, "w")
            file.write(content)
        except FileNotFoundError:
            print ("Report file ", new_file_path, "cannot be created!")
        finally:
            file.close()
        
        return new_file_path

    
    def GetUrls(self, html_text):
        urls = []
        soup = BeautifulSoup(html_text, "html.parser")
        for a in soup.findAll('a'):
            url = a['href']
            if url.find('output') != -1:
                urls.append(url)
        return urls

    
    def CopyFiles(self, paths):
        
        old_to_new_path_map = dict()
        report_dir, report_name = os.path.split(self.report)

        for old_file_path in paths:
            old_file_dir, old_file_name = os.path.split(old_file_path)
            uuid_dir = str(uuid.uuid4())
            new_local_path = os.path.join(uuid_dir, old_file_name)
            new_file_dir = os.path.join(report_dir, self.temp_dir, uuid_dir)

            if not os.path.isdir(new_file_dir):
                os.makedirs(new_file_dir)
                
            new_file_path = os.path.join(new_file_dir, old_file_name)
            
            try:
                print('Copy ', new_file_path, ' to ', new_file_path)
                shutil.copy2(old_file_path, new_file_path)
            except FileNotFoundError:
                print ("Test application output ", old_file_path, "cannot be found")
                
            old_to_new_path_map[old_file_path] = new_local_path
            
        return old_to_new_path_map

        
    def UpdateReport(self, html_text, urls_map):
        soup = BeautifulSoup(html_text, "html.parser")
        for a in soup.findAll('a'):
            url = a['href']
            if url.find('output') != -1:
                a['href'] = urls_map[url]
        return str(soup) 

        
    def Archive(self, file_to_archive_path):
        file_dir, file_name = os.path.split(file_to_archive_path)
        report_dir, report_name = os.path.split(self.report)
        file_name, file_extension = os.path.splitext(file_name)
        file_path = os.path.join(report_dir, file_name)
        
        shutil.make_archive(file_path, "zip", file_dir)
        shutil.rmtree(os.path.join(report_dir, self.temp_dir))
        return file_name

        
    def Parse(self):
        html_text = self.ReadFile()
        print ('Reading report file. OK')
        
        print ('Copying test outputs:')
        urls = self.GetUrls(html_text)
        urls_map = self.CopyFiles(urls)
        
        new_html_text = self.UpdateReport(html_text, urls_map)
        new_file_path = self.WriteFile(new_html_text)
        print('Updating report file. OK')
        
        self.Archive(new_file_path)
        print ('Archiving report. OK')
        
        print ('New report generated. OK')
        
            
    def __init__(self, reportPath):
        '''
        Constructor
        '''
        self.report = reportPath
        
        
def main(argv):
    print ("DPTechnology test app report parser")
    
    reportFilePath = ''
    try:
        opts, args = getopt.getopt(argv, "h:r:",["reportFile="])
        if (len(opts) != 1):
            raise getopt.GetoptError("Invalid number of required arguments")
    except getopt.GetoptError:
        print ("Looks like you got confused with arguments:")
        print ("parser.py -r <path to report file>")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print ("parser.py -t <path to test suite> -r <path to report file>")
            sys.exit()
        elif opt in ("-r", "--reportFile"):
            reportFilePath = arg
    
    print ('Parsing report file: ', reportFilePath)
        
    p = Parser(reportFilePath)
    p.Parse()

if __name__ == '__main__':    
    main(sys.argv[1:])