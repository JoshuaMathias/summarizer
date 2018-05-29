import yaml

class SummaryConfig():
    DEFAULT_AQUAINT1_DIRECTORY = '/opt/dropbox/17-18/573/AQUAINT'
    DEFAULT_AQUAINT2_DIRECTORY = '/opt/dropbox/17-18/573/AQUAINT-2'
    # DEFAULT_AQUAINT_DOC_DIR = '/opt/dropbox/17-18/573/Data/Documents/devtest'
    DEFAULT_AQUAINT_DOC_DIR = None
    DEFAULT_TEST_TOPIC_INDEX = '/opt/dropbox/17-18/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml'
    DEFAULT_TRAIN_TOPIC_INDEX = '/opt/dropbox/17-18/573/Data/Documents/training/2009/UpdateSumm09_test_topics.xml'
    SHELVE_DB_DEV = 'shelve_db_dev'
    SHELVE_DB_TRAIN = 'shelve_db_train'
    SHELVE_DB_TEST = 'shelve_db_test'

    DEFAULT_SUMMARY_DIR = 'outputs/D2'
    DEFAULT_RESULTS_DIR = 'outputs/results'
    DEFAULT_MAX_WORDS = 100
    DEFAULT_WORD_COUNTS_FILE = 'word_counts.txt'

    DEFAULT_TEAM_ID = 9
    DEFAULT_RELEASE_TITLE = 'Naruto ++'

    def __init__(self, config_file):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        self.cfg = cfg # lets keep this around, will be useful. jgreve
        self.TEAM_ID = self.__read_config_val_2__(cfg,
                                                  'project',
                                                  'team_id',
                                                  SummaryConfig.DEFAULT_TEAM_ID)
        self.RELEASE_TITLE = self.__read_config_val_2__(cfg,
                                                        'project',
                                                        'release_title',
                                                        SummaryConfig.DEFAULT_RELEASE_TITLE)
        self.AQUAINT1_DIRECTORY = self.__read_config_val_2__(cfg,
                                                             'aquaint',
                                                             'aquaint1_directory',
                                                             SummaryConfig.DEFAULT_AQUAINT1_DIRECTORY)
        self.AQUAINT2_DIRECTORY = self.__read_config_val_2__(cfg,
                                                             'aquaint',
                                                             'aquaint2_directory',
                                                             SummaryConfig.DEFAULT_AQUAINT2_DIRECTORY)
        self.AQUAINT_DOC_DIRECTORY = self.__read_config_val_2__(cfg,
                                                                'aquaint',
                                                                'aquaint_doc_dir',
                                                                SummaryConfig.DEFAULT_AQUAINT_DOC_DIR)
        self.AQUAINT_TEST_TOPIC_INDEX_FILE = self.__read_config_val_2__(cfg,
                                                                   'aquaint',
                                                                   'aquaint_test_topic_index',
                                                                   SummaryConfig.DEFAULT_TEST_TOPIC_INDEX)
        self.AQUAINT_TRAIN_TOPIC_INDEX_FILE = self.__read_config_val_2__(cfg,
                                                                   'aquaint',
                                                                   'aquaint_train_topic_index',
                                                                   SummaryConfig.DEFAULT_TRAIN_TOPIC_INDEX)
        self.SHELVE_DB_DEV = self.__read_config_val_2__(cfg,
                                                                   'aquaint',
                                                                   'shelve_db_dev',
                                                                   SummaryConfig.SHELVE_DB_DEV)
        self.SHELVE_DB_TRAIN = self.__read_config_val_2__(cfg,
                                                                   'aquaint',
                                                                   'shelve_db_train',
                                                                   SummaryConfig.SHELVE_DB_TRAIN)
        self.SHELVE_DB_TEST = self.__read_config_val_2__(cfg,
                                                                   'aquaint',
                                                                   'shelve_db_test',
                                                                   SummaryConfig.SHELVE_DB_TEST)
        self.OUTPUT_SUMMARY_DIRECTORY = self.__read_config_val_2__(cfg,
                                                                   'output',
                                                                   'summary_dir',
                                                                   SummaryConfig.DEFAULT_SUMMARY_DIR)
        self.OUTPUT_RESULTS_DIRECTORY = self.__read_config_val_2__(cfg,
                                                                   'output',
                                                                   'results_dir',
                                                                   SummaryConfig.DEFAULT_RESULTS_DIR)
        self.WORD_COUNTS_FILE = self.__read_config_val_2__(cfg,
                                                       'output',
                                                       'word_counts_file',
                                                       SummaryConfig.DEFAULT_WORD_COUNTS_FILE)
        self.MAX_WORDS = self.__read_config_val_2__(cfg,
                                                    'project',
                                                    'max_words',
                                                    SummaryConfig.DEFAULT_MAX_WORDS)

        self.AQUAINT = 'aquaint' in cfg
        self.ONE_FILE = 'one_file' in cfg and self.AQUAINT == False

        self.ARTICLE_FILE = self.__read_config_val_2__(cfg,
                                                       'one_file',
                                                       'article_file',
                                                       '')

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

    # def aquaint_topic_file_path(self):
    #     if self.AQUAINT_DOC_DIRECTORY is not None and len(self.AQUAINT_DOC_DIRECTORY.strip()) > 0:
    #         return self.AQUAINT_DOC_DIRECTORY + "/" + self.AQUAINT_TOPIC_INDEX_FILE
    #     else:
    #         return self.AQUAINT_TOPIC_INDEX_FILE
