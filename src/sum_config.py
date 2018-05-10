import yaml
import local_util as u

class SummaryConfig():
    DEFAULT_AQUAINT1_DIRECTORY = '/opt/dropbox/17-18/573/AQUAINT'
    DEFAULT_AQUAINT2_DIRECTORY = '/opt/dropbox/17-18/573/AQUAINT-2'
    DEFAULT_AQUAINT_DOC_DIR = '/opt/dropbox/17-18/573/Data/Documents/devtest'
    DEFAULT_TOPIC_INDEX = 'GuidedSumm10_test_topics.xml'

    DEFAULT_SUMMARY_DIR = 'outputs/D3'
    DEFAULT_RESULTS_DIR = 'outputs/results'

    DEFAULT_TEAM_ID = 9
    DEFAULT_RELEASE_TITLE = 'Naruto ++'
    DEFAULT_MAX_WORDS = 100

    def __str__( self ):
        return 'SummaryConfig(file="{}")'.format( self.cfg_file )
        self.cfg_file = config_file # because we may want to know where our values came from.

    def __init__(self, config_file):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        self.cfg = cfg # let's keep this around, it is a perfectly servicable data structure.
        self.cfg_file = config_file # because we may want to know where our values came from.
        u.eprint('__init__: cfg={}'.format( cfg ) )

        #self.AQUAINT1_DIRECTORY = self.__read_config_val_2__(cfg,
        #                                                     'aquaint',
        #                                                     'aquaint1_directory',
        #                                                     SummaryConfig.DEFAULT_AQUAINT1_DIRECTORY)
        #self.AQUAINT2_DIRECTORY = self.__read_config_val_2__(cfg,
        #                                                     'aquaint',
        #                                                     'aquaint2_directory',
        #                                                     SummaryConfig.DEFAULT_AQUAINT2_DIRECTORY)
        #self.AQUAINT_DOC_DIRECTORY = self.__read_config_val_2__(cfg,
        #                                                        'aquaint',
        #                                                        'aquaint_doc_dir',
        #                                                        SummaryConfig.DEFAULT_AQUAINT_DOC_DIR)
        #self.AQUAINT_TOPIC_INDEX_FILE = self.__read_config_val_2__(cfg,
        #                                                           'aquaint',
        #                                                           'aquaint_topic_index',
        #                                                           SummaryConfig.DEFAULT_TOPIC_INDEX)
        #self.OUTPUT_SUMMARY_DIRECTORY = self.__read_config_val_2__(cfg,
        #                                                           'output',
        #                                                           'summary_dir',
        #                                                           SummaryConfig.DEFAULT_SUMMARY_DIR)
        #self.OUTPUT_RESULTS_DIRECTORY = self.__read_config_val_2__(cfg,
        #                                                           'output',
        #                                                           'results_dir',
        #                                                           SummaryConfig.DEFAULT_RESULTS_DIR)
        #self.TEAM_ID = self.__read_config_val_2__(cfg,
        #                                          'project',
        #                                          'team_id',
        #                                          SummaryConfig.DEFAULT_TEAM_ID)
        #self.RELEASE_TITLE = self.__read_config_val_2__(cfg,
        #                                                'project',
        #                                                'release_title',
        #                                                SummaryConfig.DEFAULT_RELEASE_TITLE)
        #self.MAX_WORDS = self.__read_config_val_2__(cfg,
        #                                            'project',
        #                                            'max_words',
        #                                            SummaryConfig.DEFAULT_MAX_WORDS)
        #------------------------------------------------------------------------------------------------
        self.AQUAINT1_DIRECTORY        = self.get( 'aquaint.aquaint1_directory',  SummaryConfig.DEFAULT_AQUAINT1_DIRECTORY)
        self.AQUAINT2_DIRECTORY        = self.get( 'aquaint.aquaint2_directory',  SummaryConfig.DEFAULT_AQUAINT2_DIRECTORY)
        self.AQUAINT_DOC_DIRECTORY     = self.get( 'aquaint.aquaint_doc_dir',     SummaryConfig.DEFAULT_AQUAINT_DOC_DIR)
        self.AQUAINT_TOPIC_INDEX_FILE  = self.get( 'aquaint.aquaint_topic_index', SummaryConfig.DEFAULT_TOPIC_INDEX)
        self.OUTPUT_SUMMARY_DIRECTORY  = self.get( 'output.summary_dir',          SummaryConfig.DEFAULT_SUMMARY_DIR)
        self.OUTPUT_RESULTS_DIRECTORY  = self.get( 'output.results_dir',          SummaryConfig.DEFAULT_RESULTS_DIR)
        self.TEAM_ID                   = self.get( 'project.team_id',             SummaryConfig.DEFAULT_TEAM_ID)
        self.RELEASE_TITLE             = self.get( 'project.release_title',       SummaryConfig.DEFAULT_RELEASE_TITLE)
        self.MAX_WORDS                 = self.get( 'project.max_words',           SummaryConfig.DEFAULT_MAX_WORDS)
        

        self.AQUAINT = 'aquaint' in cfg
        self.ONE_FILE = 'one_file' in cfg and self.AQUAINT == False

        self.ARTICLE_FILE = self.__read_config_val_2__(cfg,
                                                       'one_file',
                                                       'article_file',
                                                       '')

        # 2018-05-10 jgreve: added some helper dirs for main folder clenaup
        # so... should we expose get( ) to the rest of the code ?
        # of the code isntead of putting it into instance vars (granted
        self.CONF_DIR      = self.get( 'conf.conf_dir'     )
        self.STATS_DIR     = self.get( 'run.stats_dir'     )
        self.LOG_DIR       = self.get( 'run.log_dir'       )
        self.SHELVE_DBNAME = self.get( 'run.shelve_dbname' )
    #-----------------------------------
    # Test configuration to read one article file only
    # one_config:
    #    article_file: aquaint_test1/nyt/1999/19990330_NYT
    #-----------------------------------
    # __init__() end.
    #-----------------------------------


    def get( self, key_path, default_value=None ):
        """ answer the value found at key_path or a default if given, otherwise fail w/ValueError(unk key_path) """
        keys = key_path.split('.')
        x = self.cfg # drill down from here (self.cfg, the original config object)
        path_stats = '' # track what we find in our path
        indent = ''
        for key in keys:
            if x is not None and key in x:
                x = x[key]
                path_stats += '<+{}>'.format(key) # + indicates key found.
            else:
                x = None # fell off the path.
                path_stats += '<-{}>'.format(key) # + indicates key not found.
                break
        # if key_path='A.B.C' then at this point,
        # x = self.conf['A']['B']['X']
        if x is not None:
            u.eprint('{}: using {}="{}"'.format(self, key_path, x ) )
            return x
        if default_value is None:
            raise ValueError( '{}: missing key & no default, key={}, matched={}'.format(self, key_path, path_stats ) )
        u.eprint('{}: key not found, default {}="{}"'.format(self, key_path, default_value) )
        return default_value 

    def __read_config_val_2__(self, cfg, label1, label2, default):
        if label1 in cfg and label2 in cfg[label1]:
            return cfg[label1][label2]
        else:
            return default

    def __read_config_val1__(self, cfg, label, default):
        if label in cfg:
            if cfg[label]:
                return cfg[label]
        else:
            return default

    def aquaint_topic_file_path(self):
        if self.AQUAINT_DOC_DIRECTORY is not None and len(self.AQUAINT_DOC_DIRECTORY.strip()) > 0:
            return self.AQUAINT_DOC_DIRECTORY + "/" + self.AQUAINT_TOPIC_INDEX_FILE
        else:
            return self.AQUAINT_TOPIC_INDEX_FILE
