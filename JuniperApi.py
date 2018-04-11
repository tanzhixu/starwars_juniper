#coding:utf-8

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import LockError
from jnpr.junos.exception import UnlockError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError

import yaml


class JuniperApi(object):
    '''
        Juniper Api
    '''

    def __init__(self, host, user, password):
        super(JuniperApi, self).__init__()
        self.host = host
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        print 'Connect to Juniper'
        try:
            self.d = Device(host=self.host, user=self.user, password=self.password)
            self.d.open()
        except ConnectError as err:
            print "Cannot connect to device: {0}".format(err)
            return

    def __bind(self):
        self.d.bind(cu=Config)

    def facts(self):
        '''
            Get Juniper Basic Message
        '''
        return self.d.facts

    def load_new(self,config):
        cfg = Config(self.d)
        cfg.load(path=config, format="text")
        self.d.close()

    def load(self, **kwargs):
        '''
            Load config from templates
        '''
        self.__bind()
        print "Loading configuration changes"
        try:
            self.d.cu.load(**kwargs)
        except (ConfigLoadError, Exception) as err:
            print "Unable to load configuration changes: {0}".format(err)
            print "Unlocking the configuration"
            self.__disconnect()
            return
        if self.d.cu.commit_check():
            self.__commit()
            print 'Configuration save success'
        self.__disconnect()
        return

    def __commit(self):
        print "Committing the configuration"
        try:
            self.d.cu.commit(comment='Loaded by example.')
        except CommitError as err:
            print "Unable to commit configuration: {0}".format(err)
            print "Unlocking the configuration"
            try:
                self.d.cu.unlock()
            except UnlockError as err:
                print "Unable to unlock configuration: {0}".format(err)
            self.d.close()
            return


    def __disconnect(self):
        print 'Closeing the connect'
        self.d.close()

    def diff(self,config):
        self.__bind()
        self.d.cu.load(path=config,merge=False,overwrite=True)
        self.d.cu.pdiff()


def main():
    juniperhost = '10.1.60.100'
    juniperuser = 'lab'
    juniperpass = 'lab123'
    juniperobj = JuniperApi(host=juniperhost, user=juniperuser, password=juniperpass)

    # juniper basic message
    # print juniperobj.facts()

    # config_conf = 'test_config.conf'
    # config_set = 'test_config.set'
    # load file to config juniper
    # juniperobj.load(config=config_set,format='set')

    config_template = 'config-template.j2'

    myvars = yaml.load(open('configuration.yaml').read())
    config = dict(template_path=config_template, template_vars=myvars, format='text', merge=False)
    juniperobj.load(**config)

if __name__ == '__main__':
    main()
